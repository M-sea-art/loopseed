"""Fail-closed finalization for One-Shotted mode."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from one_shotted_audit import _validation_data
from one_shotted_io import read_json, write_json_atomic
from one_shotted_types import VERSION, OneShottedError, utc_now
from one_shotted_validate import final_report_errors, validate


def finalize(root: Path) -> dict[str, Any]:
    report, data = _validation_data(root)
    if not report["ok"]:
        raise OneShottedError("Cannot finalize an invalid run: " + "; ".join(report["errors"]))
    state = data["state"]
    if str(state.get("status", "")).upper() != "ACTIVE":
        raise OneShottedError("Only an ACTIVE run can be finalized")
    gates = data["gates"]
    required = [gate for gate in gates.values() if gate.get("required", True)]
    if not required:
        raise OneShottedError("At least one required acceptance gate is necessary")
    not_passed = [str(gate.get("id")) for gate in required if str(gate.get("status", "")).upper() != "PASS"]
    if not_passed:
        raise OneShottedError("Required gates are not PASS: " + ", ".join(not_passed))
    if data["blocking_open_defects"]:
        raise OneShottedError("Open P0/P1 defects block finalization: " + ", ".join(data["blocking_open_defects"]))

    target: Path = data["target"]
    finished_at = utc_now()
    final_report = {
        "schema_version": "1.1",
        "loopseed_version": VERSION,
        "mode": "one-shotted",
        "run_id": data["goal"].get("run_id"),
        "root_goal": data["goal"].get("root_goal"),
        "verdict": "VERIFIED",
        "required_gates": [str(gate.get("id")) for gate in required],
        "gate_evidence": {str(gate.get("id")): gate.get("evidence_ids", []) for gate in required},
        "binding": state.get("binding"),
        "open_blocking_defects": [],
        "finished_at": finished_at,
    }
    final_state = deepcopy(state)
    final_state.update(
        {
            "status": "VERIFIED",
            "phase": "FINALIZE",
            "next_action": "None. Required acceptance gates are independently verified.",
            "verified_at": finished_at,
            "updated_at": finished_at,
        }
    )
    precommit_errors = final_report_errors(data, final_report, state=final_state)
    if precommit_errors:
        raise OneShottedError("Final report precommit validation failed: " + "; ".join(precommit_errors))

    report_path = target / "final-report.json"
    state_path = target / "state.json"
    previous_report = read_json(report_path) if report_path.is_file() else None
    try:
        write_json_atomic(report_path, final_report)
        write_json_atomic(state_path, final_state)
        final_validation = validate(root, require_final=True)
        if not final_validation["ok"]:
            raise OneShottedError(
                "Final-state validation failed: " + "; ".join(final_validation["errors"])
            )
    except Exception as exc:
        rollback_errors: list[str] = []
        try:
            write_json_atomic(state_path, state)
        except Exception as rollback_exc:  # pragma: no cover - catastrophic filesystem failure
            rollback_errors.append(f"state rollback failed: {rollback_exc}")
        try:
            if previous_report is None:
                report_path.unlink(missing_ok=True)
            else:
                write_json_atomic(report_path, previous_report)
        except Exception as rollback_exc:  # pragma: no cover - catastrophic filesystem failure
            rollback_errors.append(f"report rollback failed: {rollback_exc}")
        message = str(exc)
        if rollback_errors:
            message += "; " + "; ".join(rollback_errors)
        raise OneShottedError(message) from exc
    return {"ok": True, "status": "VERIFIED", "phase": "FINALIZE", "final_report": str(target / "final-report.json")}
