"""Append-only defect events for One-Shotted mode."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from one_shotted_io import append_jsonl, load_run, locked_mutation, write_json_atomic
from one_shotted_types import (
    VALID_DEFECT_STATUSES,
    VALID_SEVERITIES,
    OneShottedError,
    clean_line,
    new_id,
    utc_now,
)

@locked_mutation
def record_defect(
    root: Path,
    defect_id: str,
    severity: str,
    status: str,
    summary: str,
    actor: str,
    evidence_id: str | None = None,
) -> dict[str, Any]:
    target, goal, _, state = load_run(root)
    if str(state.get("status", "")).upper() not in {"ACTIVE", "BLOCKED"}:
        raise OneShottedError("Defects cannot be changed after a terminal result")
    severity = severity.strip().upper()
    status = status.strip().upper()
    if severity not in VALID_SEVERITIES:
        raise OneShottedError(f"severity must be one of {sorted(VALID_SEVERITIES)}")
    if status not in VALID_DEFECT_STATUSES:
        raise OneShottedError(f"status must be one of {sorted(VALID_DEFECT_STATUSES)}")
    defect_id = clean_line(defect_id, name="defect id")
    summary = clean_line(summary, name="defect summary")
    actor = clean_line(actor, name="defect actor")

    entry = {
        "id": new_id("DEFECT-EVENT"),
        "run_id": goal.get("run_id"),
        "defect_id": defect_id,
        "severity": severity,
        "status": status,
        "summary": summary,
        "actor": actor,
        "evidence_id": evidence_id or "",
        "created_at": utc_now(),
    }
    append_jsonl(target / "defects.jsonl", entry)
    if status == "OPEN" and severity in {"P0", "P1"}:
        state["phase"] = "REPAIR"
        state["next_action"] = f"Resolve {severity} defect {defect_id} and independently reverify affected gates."
        state["updated_at"] = entry["created_at"]
        write_json_atomic(target / "state.json", state)
    return {"ok": True, "defect_id": defect_id, "severity": severity, "status": status}

