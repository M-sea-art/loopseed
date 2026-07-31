"""Public validation command for One-Shotted mode."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from one_shotted_audit import _validation_data


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

        gates = data["gates"]
        required = [gate for gate in gates.values() if gate.get("required", True)]
        if not required:
            errors.append("Finalization requires at least one required acceptance gate")
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
        if str(data["state"].get("status", "")).upper() != "VERIFIED":
            errors.append("Final state must be VERIFIED")
        if str(data["state"].get("phase", "")).upper() != "FINALIZE":
            errors.append("Final phase must be FINALIZE")
        if not (data["target"] / "final-report.json").is_file():
            errors.append("Finalization requires final-report.json")
    report["errors"] = errors
    report["ok"] = not errors
    return report
