"""Bounded state transitions and stall rerouting for One-Shotted mode."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from one_shotted_bind import assert_same_binding, make_binding
from one_shotted_io import load_run, write_json_atomic
from one_shotted_types import ALLOWED_TRANSITIONS, VALID_PHASES, OneShottedError, clean_line, new_id, utc_now


def transition(
    root: Path,
    phase: str | None = None,
    next_action: str | None = None,
    no_progress: bool = False,
    blocked_reason: str | None = None,
    unblock_condition: str | None = None,
    abort: bool = False,
    project_id: str | None = None,
    candidate_commit: str | None = None,
    artifact: str | None = None,
) -> dict[str, Any]:
    target, _, _, state = load_run(root)
    status = str(state.get("status", "")).upper()
    current_phase = str(state.get("phase", "")).upper()
    if status != "ACTIVE":
        raise OneShottedError(f"Cannot transition a run in non-active status {status}")

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
        supplied_binding = [project_id, candidate_commit, artifact]
        if any(supplied_binding) and not all(supplied_binding):
            raise OneShottedError("C1 BLOCKED binding requires --project, --candidate, and --artifact together")

        existing_binding = state.get("binding")
        binding: dict[str, Any] | None = existing_binding if isinstance(existing_binding, dict) else None
        if all(supplied_binding):
            proposed = make_binding(root, str(project_id), str(candidate_commit), str(artifact))
            if binding is not None:
                assert_same_binding(binding, proposed)
            else:
                binding = proposed
                state["binding"] = binding

        blocked_at = utc_now()
        blocker: dict[str, Any] = {
            "id": new_id("BLK"),
            "reason": clean_line(blocked_reason, name="blocker reason"),
            "unblock_condition": clean_line(unblock_condition, name="unblock condition"),
            "blocked_at": blocked_at,
            "resume_phase": current_phase,
            "status": "OPEN",
        }
        if binding is not None:
            blocker["binding"] = binding
        state.update(
            {
                "status": "BLOCKED",
                "true_blocker": blocker,
                "next_action": "Wait for the exact unblock condition; resume only with fresh machine evidence.",
                "updated_at": blocked_at,
            }
        )
        write_json_atomic(target / "state.json", state)
        return {
            "ok": True,
            "status": "BLOCKED",
            "phase": current_phase,
            "blocker_id": blocker["id"],
            "true_blocker": blocker,
        }

    desired = phase.strip().upper() if phase else current_phase
    if desired not in VALID_PHASES:
        raise OneShottedError(f"phase must be one of {sorted(VALID_PHASES)}")
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
            desired = "PLAN"
            reroute_required = True
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
