"""Bounded state transitions and stall rerouting for One-Shotted mode."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from one_shotted_io import load_run, read_json, write_json_atomic
from one_shotted_tasks import TASK_GRAPH_FILE, scheduler_snapshot, task_graph_errors
from one_shotted_types import ALLOWED_TRANSITIONS, VALID_PHASES, OneShottedError, clean_line, utc_now


def transition(
    root: Path,
    phase: str | None = None,
    next_action: str | None = None,
    no_progress: bool = False,
    blocked_reason: str | None = None,
    unblock_condition: str | None = None,
    abort: bool = False,
) -> dict[str, Any]:
    target, goal, _, state = load_run(root)
    status = str(state.get("status", "")).upper()
    current_phase = str(state.get("phase", "")).upper()
    if status != "ACTIVE":
        raise OneShottedError(f"Cannot transition a run in terminal status {status}")

    if abort:
        state.update(
            {
                "status": "ABORTED",
                "next_action": "None. The owner explicitly aborted the run.",
                "updated_at": utc_now(),
            }
        )
        write_json_atomic(target / "state.json", state)
        return {"ok": True, "status": "ABORTED", "phase": current_phase}

    if bool(blocked_reason) != bool(unblock_condition):
        raise OneShottedError("BLOCKED requires both --blocker and --unblock")
    if blocked_reason and unblock_condition:
        graph_path = target / TASK_GRAPH_FILE
        if graph_path.is_file():
            graph = read_json(graph_path)
            graph_errors = task_graph_errors(graph, str(goal.get("run_id", "")))
            if graph_errors:
                raise OneShottedError("Cannot block an invalid task graph: " + "; ".join(graph_errors))
            scheduler = scheduler_snapshot(graph)
            remaining_internal_work = (
                scheduler["runnable_task_ids"]
                + scheduler["running_task_ids"]
                + scheduler["failed_task_ids"]
            )
            if remaining_internal_work:
                raise OneShottedError(
                    "Cannot mark the whole run BLOCKED while internal work remains: "
                    + ", ".join(remaining_internal_work)
                )
        state.update(
            {
                "status": "BLOCKED",
                "true_blocker": {
                    "reason": clean_line(blocked_reason, name="blocker reason"),
                    "unblock_condition": clean_line(unblock_condition, name="unblock condition"),
                },
                "next_action": "Wait for the exact unblock condition; do not claim completion.",
                "updated_at": utc_now(),
            }
        )
        write_json_atomic(target / "state.json", state)
        return {
            "ok": True,
            "status": "BLOCKED",
            "phase": current_phase,
            "true_blocker": state["true_blocker"],
        }

    desired = phase.strip().upper() if phase else current_phase
    if desired not in VALID_PHASES:
        raise OneShottedError(f"phase must be one of {sorted(VALID_PHASES)}")
    if current_phase == "CALIBRATE" and desired != "CALIBRATE":
        raise OneShottedError("Use lock-brief to leave CALIBRATE; a phase transition cannot bypass user-authorized creative lock")
    if desired != current_phase and desired not in ALLOWED_TRANSITIONS.get(current_phase, set()):
        raise OneShottedError(f"Invalid phase transition: {current_phase} -> {desired}")
    if desired == "FINALIZE":
        raise OneShottedError("Use finalize; phase FINALIZE is controlled by the final gate")

    state["round"] = int(state.get("round", 0)) + 1
    reroute_required = False
    if no_progress:
        state["no_progress_rounds"] = int(state.get("no_progress_rounds", 0)) + 1
        maximum = int(state.get("max_no_progress_rounds", 2))
        if state["no_progress_rounds"] >= maximum:
            reroute_required = True
            if current_phase == "CALIBRATE":
                desired = "CALIBRATE"
                next_action = (
                    "Stop repeating discovery questions. Present the strongest synthesis, explain the remaining material tradeoff with 2-4 options and a recommendation, then lock the brief from the user's answer."
                )
            else:
                desired = "PLAN"
                next_action = (
                    "Stop repeating the current route. Re-diagnose the root cause, compare a materially different route, "
                    "and update the plan before implementation."
                )
    else:
        state["no_progress_rounds"] = 0

    state["phase"] = desired
    if next_action:
        state["next_action"] = clean_line(next_action, name="next action")
    state["updated_at"] = utc_now()
    write_json_atomic(target / "state.json", state)
    return {
        "ok": True,
        "status": "ACTIVE",
        "phase": desired,
        "round": state["round"],
        "no_progress_rounds": state["no_progress_rounds"],
        "reroute_required": reroute_required,
        "next_action": state.get("next_action", ""),
    }
