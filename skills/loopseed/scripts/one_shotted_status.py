"""Compact One-Shotted run status."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from one_shotted_audit import _validation_data
from one_shotted_types import VALID_GATE_STATUSES

def status(root: Path) -> dict[str, Any]:
    report, data = _validation_data(root)
    if not data:
        return report
    gates = data["gates"]
    counts = {status: 0 for status in sorted(VALID_GATE_STATUSES)}
    for gate in gates.values():
        value = str(gate.get("status", "PENDING")).upper()
        counts[value] = counts.get(value, 0) + 1
    return {
        "ok": report["ok"],
        "run_id": data["goal"].get("run_id"),
        "root_goal": data["goal"].get("root_goal"),
        "status": data["state"].get("status"),
        "phase": data["state"].get("phase"),
        "round": data["state"].get("round"),
        "next_action": data["state"].get("next_action"),
        "gate_counts": counts,
        "blocking_open_defects": data["blocking_open_defects"],
        "errors": report["errors"],
        "warnings": report["warnings"],
    }
