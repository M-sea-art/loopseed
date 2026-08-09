"""Artifact and repository identity helpers for fail-closed evidence."""

from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path
from typing import Any

from one_shotted_types import OneShottedError


def resolve_artifact(root: Path, value: str) -> Path:
    root_resolved = root.expanduser().resolve()
    raw = Path(value).expanduser()
    unresolved = raw if raw.is_absolute() else root_resolved / raw
    absolute_unresolved = Path(os.path.abspath(unresolved))
    try:
        lexical_relative = absolute_unresolved.relative_to(root_resolved)
    except ValueError:
        lexical_relative = None
    if lexical_relative is not None:
        cursor = root_resolved
        for part in lexical_relative.parts:
            cursor = cursor / part
            if cursor.is_symlink():
                raise OneShottedError(
                    f"Verification artifacts may not use symlink paths: {cursor}"
                )
    path = absolute_unresolved.resolve()
    try:
        relative = path.relative_to(root_resolved)
    except ValueError as exc:
        raise OneShottedError(
            f"Artifact must remain within the project root {root_resolved}: {path}"
        ) from exc
    if not path.exists():
        raise OneShottedError(f"Artifact does not exist: {path}")
    if not path.is_file() and not path.is_dir():
        raise OneShottedError(f"Artifact must be a file or directory: {path}")
    if relative == Path(".") or (relative.parts and relative.parts[0] in {".git", ".loopseed"}):
        raise OneShottedError(
            "Verification artifacts must not be the project root or LoopSeed/Git control data"
        )
    return path


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _hash_directory(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(path.rglob("*")):
        if child.is_symlink():
            raise OneShottedError(f"Artifact directories may not contain symlinks: {child}")
        if not child.is_file():
            continue
        relative = child.relative_to(path).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(_hash_file(child).encode("ascii"))
    return digest.hexdigest()


def artifact_identity(root: Path, value: str) -> dict[str, Any]:
    root_resolved = root.expanduser().resolve()
    path = resolve_artifact(root_resolved, value)
    return {
        "path": path.relative_to(root_resolved).as_posix(),
        "kind": "directory" if path.is_dir() else "file",
        "sha256": _hash_directory(path) if path.is_dir() else _hash_file(path),
    }


def artifact_subject(item: Any) -> tuple[str, str, str] | None:
    if not isinstance(item, dict):
        return None
    path = str(item.get("path", "")).strip()
    kind = str(item.get("kind", "")).strip()
    digest = str(item.get("sha256", "")).strip()
    if not path or kind not in {"file", "directory"} or len(digest) != 64:
        return None
    return path, kind, digest


def assert_artifact_matches(root: Path, expected: dict[str, Any]) -> dict[str, Any]:
    subject = artifact_subject(expected)
    if subject is None:
        raise OneShottedError("Bound artifact requires path, kind, and sha256")
    current = artifact_identity(root, subject[0])
    if artifact_subject(current) != subject:
        raise OneShottedError(
            f"Artifact drift detected for {subject[0]}: expected {subject[2]}, got {current['sha256']}"
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
    """Return independently observed Git identity, or a non-Git receipt."""

    try:
        inside = _git(root, "rev-parse", "--is-inside-work-tree")
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        return {
            "detected": False,
            "head": None,
            "toplevel": None,
            "worktree_dirty": None,
            "tracked_worktree_dirty": None,
        }
    if inside.returncode != 0 or inside.stdout.strip().lower() != "true":
        return {
            "detected": False,
            "head": None,
            "toplevel": None,
            "worktree_dirty": None,
            "tracked_worktree_dirty": None,
        }
    try:
        top = _git(root, "rev-parse", "--show-toplevel")
        head = _git(root, "rev-parse", "HEAD")
        status = _git(root, "status", "--porcelain")
        # LoopSeed's control plane and many build outputs are intentionally
        # untracked.  The integrity boundary is stricter for tracked content:
        # it must be represented by the bound commit before and after a
        # verifier runs.
        tracked_status = _git(
            root,
            "status",
            "--porcelain",
            "--untracked-files=no",
            "--",
            ".",
            ":(exclude).loopseed",
            ":(exclude).loopseed/**",
        )
        untracked = _git(
            root,
            "ls-files",
            "--others",
            "--exclude-standard",
            "-z",
            "--",
            ".",
            ":(exclude).loopseed",
            ":(exclude).loopseed/**",
        )
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        return {
            "detected": False,
            "head": None,
            "toplevel": None,
            "worktree_dirty": None,
            "tracked_worktree_dirty": None,
        }
    return {
        "detected": True,
        "head": head.stdout.strip() if head.returncode == 0 else None,
        "toplevel": top.stdout.strip() if top.returncode == 0 else None,
        "worktree_dirty": bool(status.stdout.strip()) if status.returncode == 0 else None,
        "tracked_worktree_dirty": (
            bool(tracked_status.stdout.strip()) if tracked_status.returncode == 0 else None
        ),
        "untracked_paths": (
            sorted(path for path in untracked.stdout.split("\0") if path)
            if untracked.returncode == 0
            else None
        ),
    }


def unexpected_untracked_paths(
    repository: dict[str, Any],
    allowed_paths: list[str] | tuple[str, ...],
) -> list[str]:
    """Return non-ignored, non-control untracked paths outside explicit artifacts."""

    paths = repository.get("untracked_paths")
    if not isinstance(paths, list):
        return ["<unavailable>"]
    allowed = [str(value).strip().strip("/") for value in allowed_paths if str(value).strip()]
    return sorted(
        str(path)
        for path in paths
        if not any(
            str(path) == candidate or str(path).startswith(candidate + "/")
            for candidate in allowed
        )
    )


def binding_subject(binding: Any) -> tuple[str, str, tuple[str, str, str]] | None:
    if not isinstance(binding, dict):
        return None
    project_id = str(binding.get("project_id", "")).strip()
    candidate_commit = str(binding.get("candidate_commit", "")).strip()
    artifact = artifact_subject(binding.get("artifact"))
    if not project_id or not candidate_commit or artifact is None:
        return None
    return project_id, candidate_commit, artifact


def assert_binding_current(
    root: Path,
    binding: dict[str, Any],
    *,
    allowed_untracked: list[str] | tuple[str, ...] = (),
) -> dict[str, Any]:
    subject = binding_subject(binding)
    if subject is None:
        raise OneShottedError("Active binding requires project, candidate commit, and artifact identity")
    artifact = assert_artifact_matches(root, binding["artifact"])
    repository = repository_identity(root)
    if binding.get("git_repository_detected") is True:
        if not repository.get("detected"):
            raise OneShottedError("Bound Git repository can no longer be independently detected")
        actual = str(repository.get("head") or "")
        if actual != subject[1]:
            raise OneShottedError(
                f"Actual Git HEAD {actual or '<missing>'} does not match bound candidate {subject[1]}"
            )
        if repository.get("tracked_worktree_dirty") is not False:
            raise OneShottedError(
                "Tracked worktree content does not match the bound Git candidate"
            )
        unexpected = unexpected_untracked_paths(
            repository, [subject[2][0], *allowed_untracked]
        )
        if unexpected:
            raise OneShottedError(
                "Untracked project content is outside the bound or evidence artifacts: "
                + ", ".join(unexpected)
            )
    return {"artifact": artifact, "repository": repository}
