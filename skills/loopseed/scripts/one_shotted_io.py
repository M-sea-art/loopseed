"""Project-local JSON and JSONL persistence for One-Shotted mode."""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any

from one_shotted_types import OneShottedError, run_dir, template_dir

def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise OneShottedError(f"Missing required file: {path}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise OneShottedError(f"Cannot read valid JSON from {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise OneShottedError(f"Expected a JSON object in {path}")
    return value


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def append_jsonl(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def read_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    values: list[dict[str, Any]] = []
    errors: list[str] = []
    if not path.exists():
        return values, [f"Missing required file: {path}"]
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return values, [f"Cannot read {path}: {exc}"]
    for line_number, raw in enumerate(lines, start=1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{line_number}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{path}:{line_number}: expected an object")
            continue
        values.append(value)
    return values, errors


def load_template_json(name: str) -> dict[str, Any]:
    return read_json(template_dir() / name)


def load_template_text(name: str) -> str:
    path = template_dir() / name
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError, UnicodeError) as exc:
        raise OneShottedError(f"Cannot read bundled template {path}: {exc}") from exc


def load_run(root: Path) -> tuple[Path, dict[str, Any], dict[str, Any], dict[str, Any]]:
    target = run_dir(root)
    return (
        target,
        read_json(target / "goal-contract.json"),
        read_json(target / "acceptance.json"),
        read_json(target / "state.json"),
    )


