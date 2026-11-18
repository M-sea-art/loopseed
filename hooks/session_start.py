"""Inject bounded resume context when LoopSeed state is active."""

from __future__ import annotations

from common import compact, emit, load_state, read_event, state_status, vision_within_deadline


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
            ".loopseed/one-shotted goal, architecture, task graph, acceptance, state, evidence, and defect files before acting. "
            "Continue the declared state machine from direct evidence. Keep one integration owner, require an "
            "independent verifier for gate verdicts, dispatch safe runnable tasks before waiting, and never write "
            "VERIFIED except through the finalizer."
        )
    elif mode == "vision":
        if not vision_within_deadline(state):
            return
        message = (
            "An authorized LoopSeed vision was saved in the project-root .loopseed.md. "
            "When continuing that vision, read the latest observation and open question and inspect the "
            "current product. Choose what is worth doing next within the current user's instructions and "
            "the remaining host Goal allowance. An owner stop or exhausted budget takes precedence."
        )
    else:
        message = (
            "LoopSeed state is ACTIVE in the project-root .loopseed.md. Read it before acting, continue from "
            "the latest direct evidence, and do not treat the state label as completion proof."
        )
    if next_action and mode != "vision":
        message += f" Current next action: {next_action}"
    emit({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": message}})


if __name__ == "__main__":
    main()
