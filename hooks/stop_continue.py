"""Request one bounded continuation while active LoopSeed acceptance is unresolved."""

from __future__ import annotations

from common import compact, emit, load_state, read_event, state_status


def main() -> None:
    event = read_event()
    _, state, mode = load_state(event.get("cwd"))
    if state_status(state) != "ACTIVE":
        return
    if event.get("stop_hook_active") is True:
        return

    next_action = compact(state.get("next_action") or state.get("next"))
    if mode == "one-shotted":
        phase = compact(state.get("phase")) or "UNKNOWN"
        reason = (
            f"LoopSeed One-Shotted remains ACTIVE in phase {phase}. Read .loopseed/one-shotted and execute the "
            "next verifiable action. A worker cannot approve its own gate. A FAIL must enter REPAIR; two "
            "no-progress rounds must trigger root-cause replanning. Before stopping, either add new evidence, "
            "finalize only after every required gate has verifier-authored PASS evidence and no open P0/P1 defect, "
            "or record an exact true blocker and unblock condition."
        )
    else:
        reason = (
            "LoopSeed remains ACTIVE. Read the project-root .loopseed.md and continue from its latest direct "
            "evidence. Mark VERIFIED only when every acceptance condition is directly satisfied; mark BLOCKED "
            "only for an exact irreplaceable permission, input, authority decision, or irreversible-risk gate."
        )
    if next_action:
        reason += f" Next verifiable action: {next_action}"
    emit({"decision": "block", "reason": reason})


if __name__ == "__main__":
    main()
