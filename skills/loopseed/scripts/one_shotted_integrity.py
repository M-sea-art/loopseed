"""Artifact and repository identity helpers for C1 evidence binding."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any

from one_shotted_types import OneShottedError


def resolve_artifact(root: Path, value: str) -> Path:
    root = root.expanduser().resolve()
    raw = Path(value).expanduser()
    path = raw if raw.is_absolute() else root / raw
    path = path.resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise OneShottedError(
            f"Artifact must remain within the project root {root}: {path}"
        ) from exc
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
    stored_path = path.relative_to(root_resolved).as_posix()
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


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root.expanduser().resolve(),
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )


def repository_identity(root: Path) -> dict[str, Any]:
    """Return actual Git identity when *root* is a real worktree.

    A directory containing a placeholder ``.git`` folder is not treated as a real
    repository. Non-Git projects remain supported; C1 only enforces HEAD equality
    when Git can independently prove the checkout identity.
    """

    try:
        inside = _git(root, "rev-parse", "--is-inside-work-tree")
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        return {
            "detected": False,
            "head": None,
            "toplevel": None,
            "worktree_dirty": None,
        }
    if inside.returncode != 0 or inside.stdout.strip().lower() != "true":
        return {
            "detected": False,
            "head": None,
            "toplevel": None,
            "worktree_dirty": None,
        }

    top = _git(root, "rev-parse", "--show-toplevel")
    head = _git(root, "rev-parse", "HEAD")
    status = _git(root, "status", "--porcelain")
    return {
        "detected": True,
        "head": head.stdout.strip() if head.returncode == 0 else None,
        "toplevel": top.stdout.strip() if top.returncode == 0 else None,
        "worktree_dirty": bool(status.stdout.strip()) if status.returncode == 0 else None,
    }
