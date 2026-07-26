"""Inject bounded resume context when LoopSeed state is active."""

from __future__ import annotations

from common import compact, emit, load_state, read_event, state_status


def main() -> None:
    event = read_event()
    _, state, mode = load_state(event.get("cwd"))
    if state_status(state) != "ACTIVE":
        return

    next_action = compact(state.get("next_action") or state.get("next"))
    if mode == "one-shotted":
        phase = compact(state.get("phase")) or "UNKNOWN"
        message = (
            f"LoopSeed One-Shotted is ACTIVE in phase {phase}. Read the project-root "
            ".loopseed/one-shotted goal, architecture, acceptance, state, evidence, and defect files before acting. "
            "Continue the declared state machine from direct evidence. Keep one integration owner, require an "
            "independent verifier for gate verdicts, and never write VERIFIED except through the finalizer."
        )
    else:
        message = (
            "LoopSeed state is ACTIVE in the project-root .loopseed.md. Read it before acting, continue from "
            "the latest direct evidence, and do not treat the state label as completion proof."
        )
    if next_action:
        message += f" Current next action: {next_action}"
    emit({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": message}})


if __name__ == "__main__":
    main()
