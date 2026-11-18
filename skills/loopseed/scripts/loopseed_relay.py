"""Read the project-root LoopSeed handoff used by the skill and lifecycle hooks."""

from __future__ import annotations

import re
from pathlib import Path

RELAY_FILENAME = ".loopseed.md"
STATE_FENCE = "loopseed-state"


def parse_fields(text: str) -> dict[str, str]:
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


def read_relay(path: Path) -> dict[str, str]:
    try:
        return parse_fields(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError):
        return {}


def is_vision_relay(path: Path) -> bool:
    return path.is_file() and not path.is_symlink() and read_relay(path).get("mode") == "vision"
