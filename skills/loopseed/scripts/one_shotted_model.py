"""Small derived views over One-Shotted contracts."""

from __future__ import annotations

from typing import Any

from one_shotted_types import OneShottedError

def gate_map(acceptance: dict[str, Any]) -> dict[str, dict[str, Any]]:
    gates = acceptance.get("gates", [])
    if not isinstance(gates, list):
        raise OneShottedError("acceptance.json field 'gates' must be an array")
    result: dict[str, dict[str, Any]] = {}
    for gate in gates:
        if not isinstance(gate, dict):
            raise OneShottedError("Every acceptance gate must be an object")
        gate_id = str(gate.get("id", "")).strip()
        if not gate_id:
            raise OneShottedError("Every acceptance gate requires a non-empty id")
        if gate_id in result:
            raise OneShottedError(f"Duplicate acceptance gate id: {gate_id}")
        result[gate_id] = gate
    return result


def latest_defects(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for item in items:
        defect_id = str(item.get("defect_id", "")).strip()
        if defect_id:
            latest[defect_id] = item
    return latest


