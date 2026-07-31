"""Public validation command for One-Shotted mode."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from one_shotted_audit import _validation_data
from one_shotted_io import read_json
from one_shotted_schema import validate_json_schema
from one_shotted_types import OneShottedError, schema_dir


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
    errors.extend(f"Final report schema: {item}" for item in validate_json_schema(final_report, schema))

    final_state = state if state is not None else data["state"]
    required = [gate for gate in data["gates"].values() if gate.get("required", True)]
    expected_gate_ids = [str(gate.get("id")) for gate in required]
    expected_evidence = {
        str(gate.get("id")): gate.get("evidence_ids", [])
        for gate in required
    }
    expected = {
        "loopseed_version": final_state.get("loopseed_version"),
        "mode": "one-shotted",
        "run_id": data["goal"].get("run_id"),
        "root_goal": data["goal"].get("root_goal"),
        "verdict": "VERIFIED",
        "required_gates": expected_gate_ids,
        "gate_evidence": expected_evidence,
        "binding": final_state.get("binding"),
        "open_blocking_defects": [],
    }
    for field, value in expected.items():
        if final_report.get(field) != value:
            errors.append(f"Final report {field} does not match the current run")

    if data["goal"].get("loopseed_version") != final_state.get("loopseed_version"):
        errors.append("Goal contract and state declare different LoopSeed versions")
    finished_at = str(final_report.get("finished_at", "")).strip()
    if finished_at != str(final_state.get("verified_at", "")).strip():
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
        gates = data["gates"]
        required = [gate for gate in gates.values() if gate.get("required", True)]
        if not required:
            errors.append("Finalization requires at least one required acceptance gate")
        not_passed = [str(gate.get("id")) for gate in required if str(gate.get("status", "")).upper() != "PASS"]
        if not_passed:
            errors.append(f"Required gates are not PASS: {', '.join(not_passed)}")
        if data["blocking_open_defects"]:
            errors.append(f"Open P0/P1 defects block finalization: {', '.join(data['blocking_open_defects'])}")
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
