"""Artifact identity and digest helpers for C1 evidence binding."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from one_shotted_types import OneShottedError


def resolve_artifact(root: Path, value: str) -> Path:
    raw = Path(value).expanduser()
    path = raw if raw.is_absolute() else root.expanduser().resolve() / raw
    path = path.resolve()
    if not path.exists():
        raise OneShottedError(f"Artifact does not exist: {path}")
    if not path.is_file() and not path.is_dir():
        raise OneShottedError(f"Artifact must be a file or directory: {path}")
    return path


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _hash_directory(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        relative = child.relative_to(path).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        file_hash = _hash_file(child).encode("ascii")
        digest.update(file_hash)
    return digest.hexdigest()


def artifact_identity(root: Path, value: str) -> dict[str, Any]:
    root_resolved = root.expanduser().resolve()
    path = resolve_artifact(root_resolved, value)
    try:
        stored_path = path.relative_to(root_resolved).as_posix()
    except ValueError:
        stored_path = str(path)
    return {
        "path": stored_path,
        "kind": "directory" if path.is_dir() else "file",
        "sha256": _hash_directory(path) if path.is_dir() else _hash_file(path),
    }


def assert_artifact_matches(root: Path, expected: dict[str, Any]) -> dict[str, Any]:
    path = str(expected.get("path", "")).strip()
    digest = str(expected.get("sha256", "")).strip()
    if not path or not digest:
        raise OneShottedError("Bound artifact requires path and sha256")
    current = artifact_identity(root, path)
    if current["sha256"] != digest:
        raise OneShottedError(
            f"Artifact drift detected for {path}: expected {digest}, got {current['sha256']}"
        )
    return current
