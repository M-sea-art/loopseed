"""Fail-closed finalization for One-Shotted mode."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from one_shotted_audit import _validation_data
from one_shotted_io import exclusive_verification_mutation, read_json, write_json_atomic
from one_shotted_tasks import (
    incomplete_required_task_ids,
    required_task_ids,
    unsettled_task_ids,
)
from one_shotted_types import VERSION, OneShottedError, utc_now
from one_shotted_validate import final_report_errors, validate


def _version_at_least(value: Any, target: tuple[int, int, int]) -> bool:
    try:
        parts = [int(part) for part in str(value).split(".")]
    except (TypeError, ValueError):
        return False
    return tuple((parts + [0, 0, 0])[:3]) >= target


@exclusive_verification_mutation
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

    v0_8 = _version_at_least(state.get("loopseed_version", VERSION), (0, 8, 0))
    hard_gates = [gate for gate in required if str(gate.get("role", "hard")).lower() == "hard"]
    bar_gates = [gate for gate in required if str(gate.get("role", "hard")).lower() == "bar"]
    if v0_8:
        if not hard_gates:
            raise OneShottedError(
                "v0.8 VERIFIED requires at least one required hard-floor gate; Gate is the floor."
            )
        if not bar_gates:
            raise OneShottedError(
                "v0.8 VERIFIED requires at least one required quality-bar gate; Bar is the ceiling. Declare it with add-gate --bar."
            )

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
    if not isinstance(data.get("verification_binding"), dict):
        raise OneShottedError(
            "Finalization requires a frozen verification binding for Git HEAD and artifact SHA-256"
        )
    task_graph = data.get("task_graph", {})
    incomplete_tasks = incomplete_required_task_ids(task_graph)
    if incomplete_tasks:
        raise OneShottedError(
            "Required tasks are not SUCCEEDED: " + ", ".join(incomplete_tasks)
        )
    unsettled_tasks = unsettled_task_ids(task_graph)
    if unsettled_tasks:
        raise OneShottedError(
            "Tasks need a terminal disposition before finalization: "
            + ", ".join(unsettled_tasks)
        )
    scheduler = data.get("scheduler", {})
    if scheduler.get("running_task_ids"):
        raise OneShottedError(
            "Running tasks must settle before finalization: "
            + ", ".join(scheduler["running_task_ids"])
        )
    if state.get("scheduler_wait") is not None:
        raise OneShottedError("A declared scheduler wait must settle before finalization")

    target: Path = data["target"]
    finished_at = utc_now()
    brief = data.get("creative_brief", {})
    final_report = {
        "schema_version": "1.3",
        "loopseed_version": state.get("loopseed_version", VERSION),
        "mode": "one-shotted",
        "run_id": data["goal"].get("run_id"),
        "root_goal": data["goal"].get("root_goal"),
        "terminal_goal": data["goal"].get("terminal_goal"),
        "project_domain": data.get("project_domain"),
        "production_mode": data.get("production_mode"),
        "creative_brief_id": brief.get("brief_id") if isinstance(brief, dict) else None,
        "verdict": "VERIFIED",
        "required_gates": [str(gate.get("id")) for gate in required],
        "hard_gates": [str(gate.get("id")) for gate in hard_gates],
        "quality_bar_gates": [str(gate.get("id")) for gate in bar_gates],
        "gate_evidence": {
            str(gate.get("id")): gate.get("evidence_ids", []) for gate in required
        },
        "verification_binding": data["verification_binding"],
        "required_tasks": required_task_ids(task_graph),
        "open_blocking_defects": [],
        "finished_at": finished_at,
    }
    final_state = deepcopy(state)
    final_state.update(
        {
            "status": "VERIFIED",
            "phase": "FINALIZE",
            "next_action": "None. Hard floors and the inspectable quality bar are independently verified.",
            "verified_at": finished_at,
            "updated_at": finished_at,
        }
    )
    precommit_errors = final_report_errors(data, final_report, state=final_state)
    if precommit_errors:
        raise OneShottedError(
            "Final report precommit validation failed: " + "; ".join(precommit_errors)
        )

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
    return {
        "ok": True,
        "status": "VERIFIED",
        "phase": "FINALIZE",
        "project_domain": data.get("project_domain"),
        "production_mode": data.get("production_mode"),
        "creative_brief_id": final_report["creative_brief_id"],
        "hard_gates": final_report["hard_gates"],
        "quality_bar_gates": final_report["quality_bar_gates"],
        "final_report": str(target / "final-report.json"),
    }
