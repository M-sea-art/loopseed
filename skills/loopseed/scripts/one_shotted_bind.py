"""Explicit project, candidate, and artifact binding for C1.1 runs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from one_shotted_integrity import artifact_identity, repository_identity
from one_shotted_io import load_run, write_json_atomic
from one_shotted_types import OneShottedError, clean_line, utc_now


def make_binding(
    root: Path,
    project_id: str,
    candidate_commit: str,
    artifact: str,
) -> dict[str, Any]:
    project_id = clean_line(project_id, name="project id")
    candidate_commit = clean_line(candidate_commit, name="candidate commit")
    subject = artifact_identity(root, artifact)
    repository = repository_identity(root)
    actual_head = repository.get("head")
    if repository.get("detected"):
        if not actual_head:
            raise OneShottedError("Cannot bind a real Git worktree without a committed HEAD")
        if str(actual_head) != candidate_commit:
            raise OneShottedError(
                f"Actual Git HEAD {actual_head} does not match bound candidate {candidate_commit}"
            )

    return {
        "schema_version": "1.1",
        "project_id": project_id,
        "candidate_commit": candidate_commit,
        "artifact": subject,
        "git_repository_detected": bool(repository.get("detected")),
        "actual_candidate_commit": actual_head,
        "worktree_dirty": repository.get("worktree_dirty"),
        "bound_at": utc_now(),
    }


def binding_subject(binding: dict[str, Any]) -> tuple[str, str, str, str]:
    artifact = binding.get("artifact")
    if not isinstance(artifact, dict):
        raise OneShottedError("Project binding is missing artifact identity")
    return (
        str(binding.get("project_id", "")),
        str(binding.get("candidate_commit", "")),
        str(artifact.get("path", "")),
        str(artifact.get("sha256", "")),
    )


def assert_same_binding(existing: dict[str, Any], proposed: dict[str, Any]) -> None:
    if binding_subject(existing) != binding_subject(proposed):
        raise OneShottedError(
            "Run is already bound to a different project, candidate, or artifact; start a fresh run"
        )


def bind_project(
    root: Path,
    project_id: str,
    candidate_commit: str,
    artifact: str,
) -> dict[str, Any]:
    target, _, _, state = load_run(root)
    if str(state.get("status", "")).upper() != "ACTIVE":
        raise OneShottedError("Project binding may only be established while the run is ACTIVE")

    proposed = make_binding(root, project_id, candidate_commit, artifact)
    existing = state.get("binding")
    if isinstance(existing, dict):
        assert_same_binding(existing, proposed)
        return {
            "ok": True,
            "status": "ACTIVE",
            "binding": existing,
            "idempotent": True,
        }

    state["binding"] = proposed
    state["next_action"] = "Declare observable gates or execute the next action against the bound candidate."
    state["updated_at"] = proposed["bound_at"]
    write_json_atomic(target / "state.json", state)
    return {
        "ok": True,
        "status": "ACTIVE",
        "binding": proposed,
        "idempotent": False,
    }
