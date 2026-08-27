"""Public validation command for One-Shotted mode."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from one_shotted_audit import _validation_data
from one_shotted_io import read_json
from one_shotted_schema import validate_json_schema
from one_shotted_tasks import incomplete_required_task_ids, required_task_ids, unsettled_task_ids
from one_shotted_types import OneShottedError, schema_dir


def _version_at_least(value: Any, target: tuple[int, int, int]) -> bool:
    try:
        parts = [int(part) for part in str(value).split(".")]
    except (TypeError, ValueError):
        return False
    return tuple((parts + [0, 0, 0])[:3]) >= target


def _gate_roles(data: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    required = [gate for gate in data["gates"].values() if gate.get("required", True)]
    hard = [gate for gate in required if str(gate.get("role", "hard")).lower() == "hard"]
    bar = [gate for gate in required if str(gate.get("role", "hard")).lower() == "bar"]
    return required, hard, bar


def final_report_errors(
    data: dict[str, Any],
    final_report: dict[str, Any],
    *,
    state: dict[str, Any] | None = None,
) -> list[str]:
    """Return schema and cross-ledger errors for a terminal receipt."""

    errors: list[str] = []
    try:
        schema = read_json(schema_dir() / "final-report.schema.json")
    except OneShottedError as exc:
        return [str(exc)]
    errors.extend(
        f"Final report schema: {item}"
        for item in validate_json_schema(final_report, schema)
    )
    final_state = state if state is not None else data["state"]
    required, hard_gates, bar_gates = _gate_roles(data)
    brief = data.get("creative_brief", {})
    expected = {
        "loopseed_version": final_state.get("loopseed_version"),
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
        "verification_binding": final_state.get("verification_binding"),
        "required_tasks": required_task_ids(data.get("task_graph", {})),
        "open_blocking_defects": [],
    }
    v0_8 = _version_at_least(final_state.get("loopseed_version"), (0, 8, 0))
    if v0_8:
        expected["hard_gates"] = [str(gate.get("id")) for gate in hard_gates]
        expected["quality_bar_gates"] = [str(gate.get("id")) for gate in bar_gates]
        if final_report.get("schema_version") != "1.3":
            errors.append("v0.8 final report requires schema_version 1.3")
    for field, value in expected.items():
        if final_report.get(field) != value:
            errors.append(f"Final report {field} does not match the current run")
    if data["goal"].get("loopseed_version") != final_state.get("loopseed_version"):
        errors.append("Goal contract and state declare different LoopSeed versions")
    if str(final_report.get("finished_at", "")).strip() != str(
        final_state.get("verified_at", "")
    ).strip():
        errors.append("Final report finished_at does not match state verified_at")
    if str(final_state.get("status", "")).upper() != "VERIFIED":
        errors.append("Final report requires state status VERIFIED")
    if str(final_state.get("phase", "")).upper() != "FINALIZE":
        errors.append("Final report requires state phase FINALIZE")
    return errors


def validate(root: Path, require_final: bool = False) -> dict[str, Any]:
    report, data = _validation_data(root)
    if not data:
        return report
    errors = list(report["errors"])
    if require_final:
        calibration = data["goal"].get("calibration", {})
        if isinstance(calibration, dict) and calibration.get("enabled", False):
            if str(calibration.get("status", "")).upper() != "LOCKED":
                errors.append("Finalization requires calibration.status=LOCKED when creative dialogue was enabled")
            brief = data.get("creative_brief", {})
            if not isinstance(brief, dict) or str(brief.get("status", "")).upper() != "LOCKED":
                errors.append("Finalization requires a locked creative-brief.json")
            if not (data["target"] / "compiled-shot.md").is_file():
                errors.append("Finalization requires compiled-shot.md for a calibrated run")

        required, hard_gates, bar_gates = _gate_roles(data)
        if not required:
            errors.append("Finalization requires at least one required acceptance gate")
        v0_8 = _version_at_least(data["state"].get("loopseed_version"), (0, 8, 0))
        if v0_8:
            if not hard_gates:
                errors.append("v0.8 finalization requires at least one required hard-floor gate")
            if not bar_gates:
                errors.append("v0.8 finalization requires at least one required quality-bar gate")
        not_passed = [
            str(gate.get("id"))
            for gate in required
            if str(gate.get("status", "")).upper() != "PASS"
        ]
        if not_passed:
            errors.append(f"Required gates are not PASS: {', '.join(not_passed)}")
        if data["blocking_open_defects"]:
            errors.append(
                f"Open P0/P1 defects block finalization: {', '.join(data['blocking_open_defects'])}"
            )
        if not isinstance(data.get("verification_binding"), dict):
            errors.append("Finalization requires a verification binding")
        incomplete_tasks = incomplete_required_task_ids(data.get("task_graph", {}))
        if incomplete_tasks:
            errors.append(
                f"Required tasks are not SUCCEEDED: {', '.join(incomplete_tasks)}"
            )
        unsettled_tasks = unsettled_task_ids(data.get("task_graph", {}))
        if unsettled_tasks:
            errors.append(
                f"Tasks need a terminal disposition before finalization: {', '.join(unsettled_tasks)}"
            )
        if str(data["state"].get("status", "")).upper() != "VERIFIED":
            errors.append("Final state must be VERIFIED")
        if str(data["state"].get("phase", "")).upper() != "FINALIZE":
            errors.append("Final phase must be FINALIZE")
        final_report_path = data["target"] / "final-report.json"
        if not final_report_path.is_file():
            errors.append("Finalization requires final-report.json")
        else:
            try:
                final_report = read_json(final_report_path)
            except OneShottedError as exc:
                errors.append(str(exc))
            else:
                errors.extend(final_report_errors(data, final_report))
    report["errors"] = errors
    report["ok"] = not errors
    return report
