"""Consistency audit for One-Shotted contracts, evidence, and defects."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from one_shotted_integrity import artifact_identity
from one_shotted_io import read_json, read_jsonl
from one_shotted_model import gate_map, latest_defects
from one_shotted_runner import PRODUCER
from one_shotted_types import (
    REQUIRED_FILES,
    VALID_GATE_STATUSES,
    VALID_PHASES,
    VALID_STATUSES,
    OneShottedError,
    run_dir,
)


def _machine_errors(item: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    evidence_id = str(item.get("id", "<unknown>"))
    required = (
        "producer",
        "purpose",
        "command",
        "cwd",
        "started_at",
        "finished_at",
        "created_at",
        "exit_code",
        "project_id",
        "candidate_commit",
        "artifact",
    )
    for field in required:
        if field not in item or item.get(field) in (None, ""):
            errors.append(f"Machine evidence {evidence_id} is missing {field}")
    if item.get("producer") != PRODUCER:
        errors.append(f"Machine evidence {evidence_id} has an unknown producer")
    if item.get("purpose") not in {"GATE", "UNBLOCK"}:
        errors.append(f"Machine evidence {evidence_id} has invalid purpose")
    try:
        exit_code = int(item.get("exit_code"))
    except (TypeError, ValueError):
        errors.append(f"Machine evidence {evidence_id} has invalid exit_code")
    else:
        expected = "PASS" if exit_code == 0 else "FAIL"
        if item.get("result") != expected:
            errors.append(f"Machine evidence {evidence_id} result does not match exit_code")
    artifact = item.get("artifact")
    if not isinstance(artifact, dict) or not str(artifact.get("path", "")).strip() or not str(
        artifact.get("sha256", "")
    ).strip():
        errors.append(f"Machine evidence {evidence_id} requires artifact path and sha256")
    return errors


def _validation_data(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    target = run_dir(root)
    errors: list[str] = []
    warnings: list[str] = []
    for name in REQUIRED_FILES:
        if not (target / name).exists():
            errors.append(f"Missing required file: {target / name}")
    try:
        goal = read_json(target / "goal-contract.json")
        acceptance = read_json(target / "acceptance.json")
        state = read_json(target / "state.json")
        experts = read_json(target / "expert-registry.json")
    except OneShottedError as exc:
        return {"ok": False, "errors": [str(exc)], "warnings": [], "run_dir": str(target)}, {}

    run_ids = {str(item.get("run_id", "")) for item in (goal, acceptance, state, experts)}
    if "" in run_ids or len(run_ids) != 1:
        errors.append("Goal, acceptance, expert registry, and state must share one non-empty run_id")
    if goal.get("mode") != "one-shotted" or state.get("mode") != "one-shotted":
        errors.append("Goal contract and state must declare mode='one-shotted'")
    if not str(goal.get("root_goal", "")).strip():
        errors.append("Goal contract requires a non-empty root_goal")

    status = str(state.get("status", "")).upper()
    phase = str(state.get("phase", "")).upper()
    if status not in VALID_STATUSES:
        errors.append(f"Invalid state status: {status!r}")
    if phase not in VALID_PHASES:
        errors.append(f"Invalid state phase: {phase!r}")
    if status == "BLOCKED":
        blocker = state.get("true_blocker")
        if not isinstance(blocker, dict) or not str(blocker.get("reason", "")).strip() or not str(
            blocker.get("unblock_condition", "")
        ).strip():
            errors.append("BLOCKED requires true_blocker.reason and true_blocker.unblock_condition")
        elif isinstance(blocker.get("binding"), dict):
            if not str(blocker.get("id", "")).strip() or not str(blocker.get("blocked_at", "")).strip():
                errors.append("C1 BLOCKED requires true_blocker.id and true_blocker.blocked_at")

    evidence, evidence_errors = read_jsonl(target / "evidence.jsonl")
    defects, defect_errors = read_jsonl(target / "defects.jsonl")
    errors.extend(evidence_errors)
    errors.extend(defect_errors)
    evidence_by_id: dict[str, dict[str, Any]] = {}
    for item in evidence:
        evidence_id = str(item.get("id", "")).strip()
        if not evidence_id:
            errors.append("Every evidence entry requires a non-empty id")
        elif evidence_id in evidence_by_id:
            errors.append(f"Duplicate evidence id: {evidence_id}")
        else:
            evidence_by_id[evidence_id] = item
        if item.get("kind") == "MACHINE":
            errors.extend(_machine_errors(item))

    try:
        gates = gate_map(acceptance)
    except OneShottedError as exc:
        errors.append(str(exc))
        gates = {}
    policy = acceptance.get("policy", {})
    binding = state.get("binding")
    last_resume_at = str(state.get("last_resume_at", "")).strip()

    for gate_id, gate in gates.items():
        gate_status = str(gate.get("status", "PENDING")).upper()
        if gate_status not in VALID_GATE_STATUSES:
            errors.append(f"Gate {gate_id} has invalid status {gate_status!r}")
        owner = str(gate.get("owner", "")).strip()
        verifier = str(gate.get("verifier", "")).strip()
        if not owner or not verifier:
            errors.append(f"Gate {gate_id} requires owner and verifier")
        if policy.get("worker_self_approval_forbidden", True) and owner == verifier:
            errors.append(f"Gate {gate_id} has the same owner and verifier")
        ids = gate.get("evidence_ids", [])
        if not isinstance(ids, list):
            errors.append(f"Gate {gate_id} evidence_ids must be an array")
            ids = []
        missing = [item for item in ids if item not in evidence_by_id]
        if missing:
            errors.append(f"Gate {gate_id} references missing evidence: {', '.join(missing)}")
        if gate_status == "PASS":
            pass_items = [
                evidence_by_id[item]
                for item in ids
                if item in evidence_by_id
                and evidence_by_id[item].get("result") == "PASS"
                and evidence_by_id[item].get("actor") == verifier
                and evidence_by_id[item].get("gate_id") == gate_id
            ]
            if not pass_items:
                errors.append(f"Gate {gate_id} is PASS without verifier-authored PASS evidence")
                continue
            if gate.get("requires_machine_evidence", False):
                machine_items = [
                    item
                    for item in pass_items
                    if item.get("kind") == "MACHINE"
                    and item.get("producer") == PRODUCER
                    and item.get("purpose") == "GATE"
                    and int(item.get("exit_code", -1)) == 0
                ]
                if not machine_items:
                    errors.append(f"Gate {gate_id} requires machine-executed PASS evidence")
                    continue
                latest = machine_items[-1]
                if not isinstance(binding, dict):
                    errors.append(f"Machine gate {gate_id} requires active project binding")
                    continue
                if str(latest.get("project_id", "")) != str(binding.get("project_id", "")):
                    errors.append(f"Gate {gate_id} machine evidence has wrong project binding")
                if str(latest.get("candidate_commit", "")) != str(binding.get("candidate_commit", "")):
                    errors.append(f"Gate {gate_id} machine evidence has wrong candidate commit")
                artifact = latest.get("artifact")
                if not isinstance(artifact, dict):
                    errors.append(f"Gate {gate_id} machine evidence is missing artifact identity")
                else:
                    try:
                        current = artifact_identity(root, str(artifact.get("path", "")))
                    except OneShottedError as exc:
                        errors.append(str(exc))
                    else:
                        if current.get("sha256") != artifact.get("sha256"):
                            errors.append(f"Gate {gate_id} machine evidence is stale after artifact drift")
                if last_resume_at and str(latest.get("created_at", "")) <= last_resume_at:
                    errors.append(f"Gate {gate_id} machine evidence predates the latest resume")

    defect_state = latest_defects(defects)
    blocking_open = sorted(
        defect_id
        for defect_id, item in defect_state.items()
        if str(item.get("status", "")).upper() == "OPEN"
        and str(item.get("severity", "")).upper() in {"P0", "P1"}
    )
    if blocking_open:
        warnings.append(f"Open P0/P1 defects: {', '.join(blocking_open)}")

    data = {
        "target": target,
        "goal": goal,
        "acceptance": acceptance,
        "state": state,
        "gates": gates,
        "evidence": evidence,
        "evidence_by_id": evidence_by_id,
        "defects": defects,
        "blocking_open_defects": blocking_open,
    }
    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "run_dir": str(target),
        "run_id": goal.get("run_id"),
        "status": status,
        "phase": phase,
        "gate_count": len(gates),
        "evidence_count": len(evidence),
        "blocking_open_defects": blocking_open,
    }, data
