"""Freeze one project, candidate commit, and primary artifact for verification."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from one_shotted_integrity import (
    artifact_identity,
    binding_subject,
    repository_identity,
    unexpected_untracked_paths,
)
from one_shotted_io import (
    current_artifact_evidence_paths,
    exclusive_verification_mutation,
    load_run,
    read_jsonl,
    write_json_atomic,
)
from one_shotted_types import OneShottedError, clean_line, new_id, utc_now


def make_binding(
    root: Path,
    project_id: str,
    candidate_commit: str,
    artifact: str,
    *,
    generation: int,
    evidence_ledger_count: int,
    allowed_untracked: list[str] | tuple[str, ...] = (),
) -> dict[str, Any]:
    project_id = clean_line(project_id, name="project id")
    candidate_commit = clean_line(candidate_commit, name="candidate commit")
    subject = artifact_identity(root, artifact)
    repository = repository_identity(root)
    actual_head = repository.get("head")
    if not repository.get("detected"):
        raise OneShottedError("Verification binding requires a real Git worktree")
    if not actual_head:
        raise OneShottedError("Cannot bind a Git worktree without a committed HEAD")
    if str(actual_head) != candidate_commit:
        raise OneShottedError(
            f"Actual Git HEAD {actual_head} does not match bound candidate {candidate_commit}"
        )
    if repository.get("tracked_worktree_dirty") is not False:
        raise OneShottedError(
            "Verification binding requires tracked worktree content to match Git HEAD"
        )
    unexpected_untracked = unexpected_untracked_paths(
        repository, [subject["path"], *allowed_untracked]
    )
    if unexpected_untracked:
        raise OneShottedError(
            "Commit or remove untracked candidate content before binding: "
            + ", ".join(unexpected_untracked)
        )
    return {
        "schema_version": "1.2",
        "binding_id": new_id("BIND"),
        "generation": generation,
        "evidence_ledger_count": evidence_ledger_count,
        "project_id": project_id,
        "candidate_commit": candidate_commit,
        "artifact": subject,
        "git_repository_detected": bool(repository.get("detected")),
        "actual_candidate_commit": actual_head,
        "worktree_dirty": repository.get("worktree_dirty"),
        "tracked_worktree_dirty": repository.get("tracked_worktree_dirty"),
        "bound_at": utc_now(),
    }


@exclusive_verification_mutation
def bind_project(root: Path, project_id: str, candidate_commit: str, artifact: str) -> dict[str, Any]:
    target, _, acceptance, state = load_run(root)
    if str(state.get("status", "")).upper() != "ACTIVE":
        raise OneShottedError("Project binding may only be established while the run is ACTIVE")
    if str(state.get("phase", "")).upper() != "VERIFY":
        raise OneShottedError(
            "Freeze the verification binding only in VERIFY, after the candidate artifact is built"
        )
    existing = state.get("verification_binding")
    previous_generation = int(existing.get("generation", 0)) if isinstance(existing, dict) else 0
    evidence, evidence_errors = read_jsonl(target / "evidence.jsonl")
    if evidence_errors:
        raise OneShottedError(
            "Cannot bind against an invalid evidence ledger: " + "; ".join(evidence_errors)
        )
    legacy_machine_gate_ids = {
        str(item.get("gate_id", ""))
        for item in evidence
        if isinstance(item.get("commands"), list)
        and any(str(command).strip() for command in item.get("commands", []))
    }
    same_subject = False
    allowed_untracked: list[str] = []
    if isinstance(existing, dict):
        requested_artifact = artifact_identity(root, artifact)
        requested_subject = (
            clean_line(project_id, name="project id"),
            clean_line(candidate_commit, name="candidate commit"),
            (
                str(requested_artifact["path"]),
                str(requested_artifact["kind"]),
                str(requested_artifact["sha256"]),
            ),
        )
        same_subject = binding_subject(existing) == requested_subject
        if same_subject:
            allowed_untracked = current_artifact_evidence_paths(
                target, acceptance, existing
            )
    proposed = make_binding(
        root,
        project_id,
        candidate_commit,
        artifact,
        generation=previous_generation + 1,
        evidence_ledger_count=len(evidence),
        allowed_untracked=allowed_untracked,
    )
    gates_need_reset = any(
        isinstance(gate, dict)
        and (
            str(gate.get("status", "PENDING")).upper() != "PENDING"
            or bool(gate.get("evidence_ids"))
        )
        for gate in acceptance.get("gates", [])
    )
    if isinstance(existing, dict):
        if same_subject and binding_subject(existing) == binding_subject(proposed):
            return {
                "ok": True,
                "status": "ACTIVE",
                "verification_binding": existing,
                "idempotent": True,
                "gates_reset": False,
            }
        state.setdefault("verification_history", []).append(existing)
    acceptance_changed = False
    if not isinstance(existing, dict):
        if acceptance.get("schema_version") != "1.2":
            acceptance["schema_version"] = "1.2"
            acceptance_changed = True
        policy = acceptance.get("policy")
        if not isinstance(policy, dict):
            policy = {}
            acceptance["policy"] = policy
            acceptance_changed = True
        if policy.get("pass_requires_machine_or_hashed_artifact") is not True:
            policy["pass_requires_machine_or_hashed_artifact"] = True
            acceptance_changed = True
        for gate in acceptance.get("gates", []):
            if not isinstance(gate, dict):
                continue
            normalized_machine = bool(
                gate.get("requires_machine_evidence", False)
                or str(gate.get("id", "")) in legacy_machine_gate_ids
            )
            if gate.get("requires_machine_evidence") is not normalized_machine:
                gate["requires_machine_evidence"] = normalized_machine
                acceptance_changed = True
    if isinstance(existing, dict) or gates_need_reset:
        now = proposed["bound_at"]
        for gate in acceptance.get("gates", []):
            if not isinstance(gate, dict):
                continue
            gate["status"] = "PENDING"
            gate["evidence_ids"] = []
            gate["updated_at"] = now
        acceptance_changed = True
    if acceptance_changed:
        write_json_atomic(target / "acceptance.json", acceptance)
    state["verification_binding"] = proposed
    state["next_action"] = (
        "Execute real acceptance gates against the frozen candidate and hashed artifact."
    )
    state["updated_at"] = proposed["bound_at"]
    write_json_atomic(target / "state.json", state)
    return {
        "ok": True,
        "status": "ACTIVE",
        "verification_binding": proposed,
        "idempotent": False,
        "gates_reset": isinstance(existing, dict) or gates_need_reset,
        "acceptance_normalized": acceptance_changed,
    }
