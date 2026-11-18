"""Shared, dependency-free helpers for LoopSeed lifecycle hooks."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# The plugin hooks and the standalone skill CLI use the same note format.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "loopseed" / "scripts"))
from loopseed_relay import RELAY_FILENAME, read_relay

ONE_SHOTTED_STATE = Path(".loopseed") / "one-shotted" / "state.json"
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


def load_state(cwd: str | None) -> tuple[Path | None, dict[str, Any], str]:
    """Give a strict run precedence until an explicit vision names its finished run."""
    root = project_root(cwd)
    if root is None:
        return None, {}, "none"

    one_shotted = root / ONE_SHOTTED_STATE
    strict_state = None
    if one_shotted.is_file():
        try:
            value = json.loads(one_shotted.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            value = {}
        strict_state = value if isinstance(value, dict) else {}
        if state_status(strict_state) not in TERMINAL_STATES:
            return one_shotted, strict_state, "one-shotted"

    relay = root / RELAY_FILENAME
    if relay.is_file():
        note = read_relay(relay)
        mode = "vision" if note.get("mode") == "vision" else "legacy"
        if strict_state is None:
            return relay, note, mode
        predecessor = note.get("after_one_shotted")
        if mode == "vision" and predecessor and predecessor == strict_state.get("run_id"):
            return relay, note, mode
    if strict_state is not None:
        return one_shotted, strict_state, "one-shotted"
    return None, {}, "none"


def state_status(state: dict[str, Any]) -> str:
    return str(state.get("status", "")).strip().upper()


def vision_within_deadline(state: dict[str, str]) -> bool:
    if "deadline_utc" not in state:
        return True
    try:
        deadline = datetime.fromisoformat(state["deadline_utc"].replace("Z", "+00:00"))
    except ValueError:
        return False
    return deadline.tzinfo is not None and datetime.now(timezone.utc) < deadline


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
