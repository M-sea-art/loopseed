"""Acceptance-gate declaration for One-Shotted mode."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from one_shotted_io import load_run, locked_mutation, write_json_atomic
from one_shotted_model import gate_map
from one_shotted_types import OneShottedError, clean_line, utc_now


@locked_mutation
def add_gate(
    root: Path,
    gate_id: str,
    title: str,
    criterion: str,
    owner: str,
    verifier: str,
    required: bool = True,
    requires_machine_evidence: bool = False,
) -> dict[str, Any]:
    target, _, acceptance, state = load_run(root)
    if str(state.get("status", "")).upper() != "ACTIVE":
        raise OneShottedError("Gates may only be changed while the run is ACTIVE")
    phase = str(state.get("phase", "")).upper()
    if phase == "CALIBRATE":
        raise OneShottedError("Lock the creative brief before declaring production acceptance gates")
    if phase not in {"BIND", "PLAN"}:
        raise OneShottedError(
            "Declare acceptance gates in BIND or PLAN, before implementation and verification"
        )

    gate_id = clean_line(gate_id, name="gate id")
    title = clean_line(title, name="gate title")
    criterion = clean_line(criterion, name="gate criterion")
    owner = clean_line(owner, name="gate owner")
    verifier = clean_line(verifier, name="gate verifier")
    if owner == verifier:
        raise OneShottedError("Implementation owner and gate verifier must be different")

    gates = gate_map(acceptance)
    if gate_id in gates:
        raise OneShottedError(f"Acceptance gate already exists: {gate_id}")
    acceptance.setdefault("gates", []).append(
        {
            "id": gate_id,
            "title": title,
            "criterion": criterion,
            "required": bool(required),
            "owner": owner,
            "verifier": verifier,
            "status": "PENDING",
            "evidence_ids": [],
            "requires_machine_evidence": bool(requires_machine_evidence),
            "updated_at": utc_now(),
        }
    )
    write_json_atomic(target / "acceptance.json", acceptance)
    return {
        "ok": True,
        "gate": gate_id,
        "required": bool(required),
        "requires_machine_evidence": bool(requires_machine_evidence),
        "status": "PENDING",
    }
