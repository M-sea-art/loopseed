"""Machine-executed evidence for C1 gate and unblock verification."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from one_shotted_integrity import artifact_identity
from one_shotted_io import append_jsonl, load_run, write_json_atomic
from one_shotted_model import gate_map
from one_shotted_types import OneShottedError, clean_line, new_id, utc_now

PRODUCER = "loopseed.machine-evidence-runner"
MAX_OUTPUT = 4000


def _bounded(value: str | None) -> str:
    text = value or ""
    return text if len(text) <= MAX_OUTPUT else text[:MAX_OUTPUT] + "\n...[truncated]"


def _assert_binding(expected: dict[str, Any], project_id: str, candidate_commit: str, artifact: dict[str, Any]) -> None:
    if str(expected.get("project_id", "")) != project_id:
        raise OneShottedError("Evidence project binding does not match the active run")
    if str(expected.get("candidate_commit", "")) != candidate_commit:
        raise OneShottedError("Evidence candidate commit does not match the active run")
    expected_artifact = expected.get("artifact")
    if not isinstance(expected_artifact, dict):
        raise OneShottedError("Active binding is missing artifact identity")
    if str(expected_artifact.get("path", "")) != str(artifact.get("path", "")):
        raise OneShottedError("Evidence artifact path does not match the active run")
    if str(expected_artifact.get("sha256", "")) != str(artifact.get("sha256", "")):
        raise OneShottedError("Evidence artifact hash does not match the active run")


def run_evidence(
    root: Path,
    actor: str,
    command: str,
    project_id: str,
    candidate_commit: str,
    artifact: str,
    *,
    gate_id: str | None = None,
    blocker_id: str | None = None,
    timeout_seconds: int = 120,
) -> dict[str, Any]:
    if bool(gate_id) == bool(blocker_id):
        raise OneShottedError("Machine evidence requires exactly one of gate_id or blocker_id")

    target, goal, acceptance, state = load_run(root)
    actor = clean_line(actor, name="evidence actor")
    command = clean_line(command, name="evidence command")
    project_id = clean_line(project_id, name="project id")
    candidate_commit = clean_line(candidate_commit, name="candidate commit")
    if timeout_seconds <= 0:
        raise OneShottedError("timeout_seconds must be positive")

    status = str(state.get("status", "")).upper()
    gates = gate_map(acceptance)
    gate: dict[str, Any] | None = None
    purpose = "UNBLOCK" if blocker_id else "GATE"

    if blocker_id:
        if status != "BLOCKED":
            raise OneShottedError("Unblock evidence may only be executed while the run is BLOCKED")
        blocker = state.get("true_blocker")
        if not isinstance(blocker, dict) or str(blocker.get("id", "")) != blocker_id:
            raise OneShottedError("Evidence blocker does not match the active blocker")
        binding = blocker.get("binding")
        if not isinstance(binding, dict):
            raise OneShottedError("Active blocker lacks C1 project binding")
    else:
        if status != "ACTIVE":
            raise OneShottedError("Gate evidence may only be executed while the run is ACTIVE")
        if gate_id not in gates:
            raise OneShottedError(f"Unknown acceptance gate: {gate_id}")
        gate = gates[str(gate_id)]
        verifier = str(gate.get("verifier", "")).strip()
        owner = str(gate.get("owner", "")).strip()
        if actor != verifier:
            raise OneShottedError(f"Gate {gate_id} evidence must be executed by verifier {verifier!r}")
        if actor == owner:
            raise OneShottedError("Implementation owner cannot self-approve a gate")
        binding = state.get("binding")
        if not isinstance(binding, dict):
            raise OneShottedError("Active run lacks C1 project binding")

    before = artifact_identity(root, artifact)
    _assert_binding(binding, project_id, candidate_commit, before)

    started_at = utc_now()
    timed_out = False
    try:
        completed = subprocess.run(
            command,
            cwd=root.expanduser().resolve(),
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        exit_code = int(completed.returncode)
        stdout = _bounded(completed.stdout)
        stderr = _bounded(completed.stderr)
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        exit_code = 124
        stdout = _bounded(exc.stdout.decode() if isinstance(exc.stdout, bytes) else exc.stdout)
        stderr = _bounded(exc.stderr.decode() if isinstance(exc.stderr, bytes) else exc.stderr)
    finished_at = utc_now()

    after = artifact_identity(root, artifact)
    evidence_id = new_id("EV")
    result = "PASS" if exit_code == 0 else "FAIL"
    entry = {
        "id": evidence_id,
        "schema_version": "1.0",
        "kind": "MACHINE",
        "producer": PRODUCER,
        "purpose": purpose,
        "run_id": goal.get("run_id"),
        "gate_id": gate_id,
        "blocker_id": blocker_id,
        "result": result,
        "actor": actor,
        "command": command,
        "cwd": str(root.expanduser().resolve()),
        "started_at": started_at,
        "finished_at": finished_at,
        "created_at": finished_at,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "stdout_summary": stdout,
        "stderr_summary": stderr,
        "project_id": project_id,
        "candidate_commit": candidate_commit,
        "artifact": after,
        "artifact_before": before,
    }
    append_jsonl(target / "evidence.jsonl", entry)

    if gate is not None:
        gate["status"] = result
        gate.setdefault("evidence_ids", []).append(evidence_id)
        gate["updated_at"] = finished_at
        write_json_atomic(target / "acceptance.json", acceptance)
        state["phase"] = "VERIFY" if result == "PASS" else "REPAIR"
        state["round"] = int(state.get("round", 0)) + 1
        state["next_action"] = (
            "Evaluate the remaining acceptance gates."
            if result == "PASS"
            else f"Repair gate {gate_id} from machine evidence {evidence_id}, then rerun it."
        )
        state["updated_at"] = finished_at
        write_json_atomic(target / "state.json", state)

    return {
        "ok": exit_code == 0,
        "evidence_id": evidence_id,
        "purpose": purpose,
        "gate": gate_id,
        "blocker": blocker_id,
        "result": result,
        "exit_code": exit_code,
        "artifact": after,
    }
