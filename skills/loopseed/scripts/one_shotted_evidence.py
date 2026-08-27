"""Verifier-authored, artifact-bound gate verdict recording."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from one_shotted_integrity import (
    artifact_identity,
    assert_binding_current,
    binding_subject,
)
from one_shotted_io import (
    append_jsonl,
    current_gate_evidence_ids,
    current_artifact_evidence_paths,
    load_run,
    locked_mutation,
    write_json_atomic,
)
from one_shotted_model import gate_map
from one_shotted_types import VALID_RESULTS, OneShottedError, clean_line, new_id, utc_now

ARTIFACT_PRODUCER = "loopseed.artifact-evidence-recorder"


@locked_mutation
def record_gate_result(
    root: Path,
    gate_id: str,
    result: str,
    actor: str,
    summary: str,
    commands: list[str] | None = None,
    artifacts: list[str] | None = None,
) -> dict[str, Any]:
    target, goal, acceptance, state = load_run(root)
    if str(state.get("status", "")).upper() != "ACTIVE":
        raise OneShottedError("Evidence may only be recorded while the run is ACTIVE")
    result = result.strip().upper()
    if result not in VALID_RESULTS:
        raise OneShottedError(f"result must be one of {sorted(VALID_RESULTS)}")
    actor = clean_line(actor, name="evidence actor")
    summary = clean_line(summary, name="evidence summary")

    gates = gate_map(acceptance)
    if gate_id not in gates:
        raise OneShottedError(f"Unknown acceptance gate: {gate_id}")
    gate = gates[gate_id]
    verifier = str(gate.get("verifier", "")).strip()
    owner = str(gate.get("owner", "")).strip()
    if actor != verifier:
        raise OneShottedError(f"Gate {gate_id} verdict must be recorded by verifier {verifier!r}")
    if actor == owner:
        raise OneShottedError("Implementation owner cannot self-approve a gate")

    command_claims = [item for item in (commands or []) if str(item).strip()]
    if command_claims:
        raise OneShottedError(
            "record does not execute commands; use run-evidence for machine verification"
        )
    artifact_values = [str(item).strip() for item in (artifacts or []) if str(item).strip()]
    artifact_receipts = [artifact_identity(root, item) for item in artifact_values]
    binding = state.get("verification_binding")
    subject = binding_subject(binding)
    repository: dict[str, Any] = {
        "detected": False,
        "head": None,
        "worktree_dirty": None,
    }
    if result == "PASS":
        if subject is None:
            raise OneShottedError(
                "PASS evidence requires a frozen verification binding; use bind first"
            )
        if not artifact_receipts:
            raise OneShottedError(
                "Observational PASS evidence requires at least one existing hashed artifact. "
                "A visual or experiential gate may be decided autonomously by its independent verifier; "
                "it does not require routine human approval."
            )
        allowed_untracked = current_artifact_evidence_paths(target, acceptance, binding)
        repository = assert_binding_current(
            root,
            binding,
            allowed_untracked=[
                *allowed_untracked,
                *(str(item["path"]) for item in artifact_receipts),
            ],
        )["repository"]

    evidence_id = new_id("EV")
    entry = {
        "id": evidence_id,
        "schema_version": "1.2",
        "kind": "ARTIFACT" if artifact_receipts else "MANUAL",
        "producer": ARTIFACT_PRODUCER,
        "run_id": goal.get("run_id"),
        "gate_id": gate_id,
        "result": result,
        "actor": actor,
        "summary": summary,
        "artifacts": artifact_receipts,
        "project_id": subject[0] if subject else None,
        "candidate_commit": subject[1] if subject else None,
        "binding_id": binding.get("binding_id") if isinstance(binding, dict) else None,
        "generation": binding.get("generation") if isinstance(binding, dict) else None,
        "actual_candidate_commit": repository.get("head"),
        "git_repository_detected": bool(repository.get("detected")),
        "worktree_dirty": repository.get("worktree_dirty"),
        "created_at": utc_now(),
    }
    append_jsonl(target / "evidence.jsonl", entry)

    gate["status"] = result
    gate["evidence_ids"] = current_gate_evidence_ids(
        target, gate_id, binding if isinstance(binding, dict) else None
    )
    gate["updated_at"] = entry["created_at"]
    write_json_atomic(target / "acceptance.json", acceptance)

    state["phase"] = "VERIFY" if result == "PASS" else "REPAIR"
    state["round"] = int(state.get("round", 0)) + 1
    state["no_progress_rounds"] = 0 if result == "PASS" else int(state.get("no_progress_rounds", 0))
    state["next_action"] = (
        "Evaluate the remaining acceptance gates."
        if result == "PASS"
        else f"Repair gate {gate_id} from evidence {evidence_id}, then have the independent verifier rerun it without returning to routine human approval."
    )
    state["updated_at"] = entry["created_at"]
    write_json_atomic(target / "state.json", state)
    return {
        "ok": True,
        "evidence_id": evidence_id,
        "gate": gate_id,
        "result": result,
        "phase": state["phase"],
        "next_action": state["next_action"],
    }
