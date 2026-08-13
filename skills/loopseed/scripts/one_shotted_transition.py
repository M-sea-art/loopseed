"""Bounded state transitions and stall rerouting for One-Shotted mode."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from one_shotted_io import load_run, locked_mutation, read_json, write_json_atomic
from one_shotted_tasks import TASK_GRAPH_FILE, scheduler_snapshot, task_graph_errors
from one_shotted_types import ALLOWED_TRANSITIONS, VALID_PHASES, OneShottedError, clean_line, utc_now


ROUTINE_HUMAN_GATE_TERMS = (
    "human review",
    "human approval",
    "human gate",
    "manual review",
    "manual approval",
    "manual gate",
    "user review",
    "user approval",
    "user confirmation",
    "owner review",
    "owner approval",
    "await user",
    "wait for user",
    "ask the user",
    "用户确认",
    "用户验收",
    "等待用户",
    "等用户",
    "人类确认",
    "人类验收",
    "人工确认",
    "人工验收",
    "人工审批",
    "视觉确认",
    "视觉验收",
)

TRUE_EXTERNAL_BLOCKER_TERMS = (
    "credential",
    "login",
    "sign in",
    "sign-in",
    "payment",
    "purchase",
    "billing",
    "legal",
    "account permission",
    "2fa",
    "two-factor",
    "secret",
    "license acceptance",
    "store submission",
    "production deployment permission",
    "publishing credential",
    "凭据",
    "登录",
    "支付",
    "付款",
    "购买",
    "账单",
    "法律",
    "账户权限",
    "验证码",
    "双重验证",
    "密钥",
    "许可接受",
    "发布权限",
    "商店提交",
)


def _is_routine_human_gate(reason: str, unblock: str) -> bool:
    text = f"{reason}\n{unblock}".casefold()
    asks_for_human_approval = any(term.casefold() in text for term in ROUTINE_HUMAN_GATE_TERMS)
    has_true_external_condition = any(term.casefold() in text for term in TRUE_EXTERNAL_BLOCKER_TERMS)
    return asks_for_human_approval and not has_true_external_condition


@locked_mutation
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
        clean_reason = clean_line(blocked_reason, name="blocker reason")
        clean_unblock = clean_line(unblock_condition, name="unblock condition")
        if current_phase != "CALIBRATE" and _is_routine_human_gate(clean_reason, clean_unblock):
            raise OneShottedError(
                "Routine human approval is not a valid production blocker after calibration. "
                "Use independent observation, playtest, critique, and evidence to decide and continue. "
                "BLOCKED is reserved for an exact external condition the run cannot satisfy itself."
            )
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
                    "reason": clean_reason,
                    "unblock_condition": clean_unblock,
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
