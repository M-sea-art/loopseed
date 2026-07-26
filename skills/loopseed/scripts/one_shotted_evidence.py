"""Independent gate verdict recording for One-Shotted mode."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from one_shotted_io import append_jsonl, load_run, write_json_atomic
from one_shotted_model import gate_map
from one_shotted_types import VALID_RESULTS, OneShottedError, clean_line, new_id, utc_now

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

    evidence_id = new_id("EV")
    entry = {
        "id": evidence_id,
        "run_id": goal.get("run_id"),
        "gate_id": gate_id,
        "result": result,
        "actor": actor,
        "summary": summary,
        "commands": [item for item in (commands or []) if item],
        "artifacts": [item for item in (artifacts or []) if item],
        "created_at": utc_now(),
    }
    append_jsonl(target / "evidence.jsonl", entry)

    gate["status"] = result
    gate.setdefault("evidence_ids", []).append(evidence_id)
    gate["updated_at"] = entry["created_at"]
    write_json_atomic(target / "acceptance.json", acceptance)

    state["phase"] = "VERIFY" if result == "PASS" else "REPAIR"
    state["round"] = int(state.get("round", 0)) + 1
    state["no_progress_rounds"] = 0 if result == "PASS" else int(state.get("no_progress_rounds", 0))
    state["next_action"] = (
        "Evaluate the remaining acceptance gates."
        if result == "PASS"
        else f"Repair gate {gate_id} from evidence {evidence_id}, then ask the independent verifier to rerun it."
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


