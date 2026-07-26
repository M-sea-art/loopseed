"""Shared, dependency-free helpers for LoopSeed lifecycle hooks."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

LEGACY_STATE_FILENAME = ".loopseed.md"
ONE_SHOTTED_STATE = Path(".loopseed") / "one-shotted" / "state.json"
STATE_FENCE = "loopseed-state"
TERMINAL_STATES = {"VERIFIED", "BLOCKED", "ABORTED"}


def read_event() -> dict[str, Any]:
    try:
        value = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return {}
    return value if isinstance(value, dict) else {}


def project_root(cwd: str | None) -> Path | None:
    if not cwd:
        return None
    try:
        current = Path(cwd).expanduser().resolve()
    except (OSError, RuntimeError):
        return None
    if not current.exists():
        return None
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current


def parse_legacy_state(text: str) -> dict[str, str]:
    pattern = re.compile(
        rf"```{re.escape(STATE_FENCE)}\s*\n(?P<body>.*?)\n```",
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        return {}
    result: dict[str, str] = {}
    for raw_line in match.group("body").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().lower()
        if key:
            result[key] = value.strip()
    return result


def load_state(cwd: str | None) -> tuple[Path | None, dict[str, Any], str]:
    """Load One-Shotted JSON first, then the legacy markdown state."""
    root = project_root(cwd)
    if root is None:
        return None, {}, "none"

    one_shotted = root / ONE_SHOTTED_STATE
    if one_shotted.is_file():
        try:
            value = json.loads(one_shotted.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            value = {}
        if isinstance(value, dict):
            return one_shotted, value, "one-shotted"

    legacy = root / LEGACY_STATE_FILENAME
    if legacy.is_file():
        try:
            return legacy, parse_legacy_state(legacy.read_text(encoding="utf-8")), "legacy"
        except (OSError, UnicodeError):
            return legacy, {}, "legacy"
    return None, {}, "none"


def state_status(state: dict[str, Any]) -> str:
    return str(state.get("status", "")).strip().upper()


def compact(value: Any, limit: int = 320) -> str:
    if value is None:
        return ""
    normalized = " ".join(str(value).split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "…"


def emit(value: dict[str, Any]) -> None:
    json.dump(value, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
