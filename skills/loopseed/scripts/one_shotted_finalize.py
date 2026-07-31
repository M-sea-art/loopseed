"""Fail-closed finalization for One-Shotted mode."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from one_shotted_audit import _validation_data
from one_shotted_io import write_json_atomic
from one_shotted_types import VERSION, OneShottedError, utc_now
from one_shotted_validate import validate


def finalize(root: Path) -> dict[str, Any]:
    report, data = _validation_data(root)
    if not report["ok"]:
        raise OneShottedError("Cannot finalize an invalid run: " + "; ".join(report["errors"]))
    state = data["state"]
    if str(state.get("status", "")).upper() != "ACTIVE":
        raise OneShottedError("Only an ACTIVE run can be finalized")

    calibration = data["goal"].get("calibration", {})
    if isinstance(calibration, dict) and calibration.get("enabled", False):
        if str(calibration.get("status", "")).upper() != "LOCKED":
            raise OneShottedError("Creative dialogue was enabled, so the user-authorized creative brief must be LOCKED before finalization")
        brief = data.get("creative_brief", {})
        if not isinstance(brief, dict) or str(brief.get("status", "")).upper() != "LOCKED":
            raise OneShottedError("Finalization requires a valid locked creative-brief.json")
        if not (data["target"] / "compiled-shot.md").is_file():
            raise OneShottedError("Finalization requires compiled-shot.md for a calibrated run")

    gates = data["gates"]
    required = [gate for gate in gates.values() if gate.get("required", True)]
    if not required:
        raise OneShottedError("At least one required acceptance gate is necessary")
    not_passed = [
        str(gate.get("id"))
        for gate in required
        if str(gate.get("status", "")).upper() != "PASS"
    ]
    if not_passed:
        raise OneShottedError("Required gates are not PASS: " + ", ".join(not_passed))
    if data["blocking_open_defects"]:
        raise OneShottedError(
            "Open P0/P1 defects block finalization: " + ", ".join(data["blocking_open_defects"])
        )

    target: Path = data["target"]
    finished_at = utc_now()
    brief = data.get("creative_brief", {})
    final_report = {
        "schema_version": "1.1",
        "loopseed_version": VERSION,
        "mode": "one-shotted",
        "run_id": data["goal"].get("run_id"),
        "root_goal": data["goal"].get("root_goal"),
        "terminal_goal": data["goal"].get("terminal_goal"),
        "project_domain": data.get("project_domain"),
        "production_mode": data.get("production_mode"),
        "creative_brief_id": brief.get("brief_id") if isinstance(brief, dict) else None,
        "verdict": "VERIFIED",
        "required_gates": [str(gate.get("id")) for gate in required],
        "gate_evidence": {
            str(gate.get("id")): gate.get("evidence_ids", []) for gate in required
        },
        "open_blocking_defects": [],
        "finished_at": finished_at,
    }
    state.update(
        {
            "status": "VERIFIED",
            "phase": "FINALIZE",
            "next_action": "None. Required acceptance gates are independently verified.",
            "verified_at": finished_at,
            "updated_at": finished_at,
        }
    )
    write_json_atomic(target / "final-report.json", final_report)
    write_json_atomic(target / "state.json", state)
    final_validation = validate(root, require_final=True)
    if not final_validation["ok"]:
        raise OneShottedError(
            "Final-state validation failed: " + "; ".join(final_validation["errors"])
        )
    return {
        "ok": True,
        "status": "VERIFIED",
        "phase": "FINALIZE",
        "project_domain": data.get("project_domain"),
        "production_mode": data.get("production_mode"),
        "creative_brief_id": final_report["creative_brief_id"],
        "final_report": str(target / "final-report.json"),
    }
