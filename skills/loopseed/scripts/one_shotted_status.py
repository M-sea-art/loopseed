"""Compact One-Shotted run status."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from one_shotted_audit import _validation_data
from one_shotted_tasks import incomplete_required_task_ids, unsettled_task_ids
from one_shotted_types import VALID_GATE_STATUSES


def status(root: Path) -> dict[str, Any]:
    report, data = _validation_data(root)
    if not data:
        return report
    gates = data["gates"]
    counts = {status: 0 for status in sorted(VALID_GATE_STATUSES)}
    role_counts = {"hard": 0, "bar": 0}
    bar_statuses: dict[str, str] = {}
    for gate in gates.values():
        value = str(gate.get("status", "PENDING")).upper()
        counts[value] = counts.get(value, 0) + 1
        role = str(gate.get("role", "hard")).lower()
        if role in role_counts:
            role_counts[role] += 1
        if role == "bar":
            bar_statuses[str(gate.get("id", ""))] = value
    calibration = data["goal"].get("calibration", {})
    brief = data.get("creative_brief", {})
    binding = data.get("verification_binding")
    return {
        "ok": report["ok"],
        "run_id": data["goal"].get("run_id"),
        "root_goal": data["goal"].get("root_goal"),
        "terminal_goal": data["goal"].get("terminal_goal"),
        "project_domain": data.get("project_domain"),
        "production_mode": data.get("production_mode"),
        "calibration_status": data.get("calibration_status"),
        "dialogue_rounds": data.get("dialogue_rounds", 0),
        "max_dialogue_rounds": calibration.get("max_rounds") if isinstance(calibration, dict) else None,
        "creative_brief_id": brief.get("brief_id") if isinstance(brief, dict) else None,
        "status": data["state"].get("status"),
        "phase": data["state"].get("phase"),
        "round": data["state"].get("round"),
        "next_action": data["state"].get("next_action"),
        "gate_counts": counts,
        "gate_role_counts": role_counts,
        "quality_bar_statuses": bar_statuses,
        "verification_binding_id": binding.get("binding_id") if isinstance(binding, dict) else None,
        "verification_generation": binding.get("generation") if isinstance(binding, dict) else None,
        "incomplete_required_task_ids": incomplete_required_task_ids(
            data.get("task_graph", {})
        ),
        "unsettled_task_ids": unsettled_task_ids(data.get("task_graph", {})),
        "runnable_task_ids": data.get("scheduler", {}).get("runnable_task_ids", []),
        "running_task_ids": data.get("scheduler", {}).get("running_task_ids", []),
        "scheduler_wait": data["state"].get("scheduler_wait"),
        "blocking_open_defects": data["blocking_open_defects"],
        "errors": report["errors"],
        "warnings": report["warnings"],
    }
