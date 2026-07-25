"""Shared, dependency-free helpers for LoopSeed lifecycle hooks."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

STATE_FILENAME = ".loopseed.md"
STATE_FENCE = "loopseed-state"
TERMINAL_STATES = {"VERIFIED", "BLOCKED", "ABORTED"}


def read_event() -> dict[str, Any]:
    """Read one hook event from stdin; malformed input becomes an empty event."""
    try:
        value = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return {}
    return value if isinstance(value, dict) else {}


def project_root(cwd: str | None) -> Path | None:
    """Return the nearest Git root, or the supplied directory for non-Git work."""
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


def find_state_file(cwd: str | None) -> Path | None:
    root = project_root(cwd)
    if root is None:
        return None

    candidate = root / STATE_FILENAME
    return candidate if candidate.is_file() else None


def parse_state(text: str) -> dict[str, str]:
    """Parse the small key=value block inside a loopseed-state fence."""
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
        normalized_key = key.strip().lower()
        normalized_value = value.strip()
        if normalized_key:
            result[normalized_key] = normalized_value
    return result


def load_state(cwd: str | None) -> tuple[Path | None, dict[str, str]]:
    path = find_state_file(cwd)
    if path is None:
        return None, {}

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return path, {}

    return path, parse_state(text)


def state_status(state: dict[str, str]) -> str:
    return state.get("status", "").strip().upper()


def compact(value: str | None, limit: int = 320) -> str:
    """Return a single-line, bounded value suitable for model-visible hook output."""
    if not value:
        return ""
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "…"


def emit(value: dict[str, Any]) -> None:
    json.dump(value, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
