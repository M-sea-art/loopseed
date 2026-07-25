"""Inject minimal resume context when a project has active LoopSeed state."""

from __future__ import annotations

from common import compact, emit, load_state, read_event, state_status


def main() -> None:
    event = read_event()
    _, state = load_state(event.get("cwd"))
    if state_status(state) != "ACTIVE":
        return

    next_action = compact(state.get("next"))
    message = (
        "LoopSeed state is ACTIVE in the project-root .loopseed.md. "
        "Read that file before acting. Continue from the latest direct evidence, "
        "keep the project plan and acceptance as authority, and do not treat the "
        "state label as completion proof."
    )
    if next_action:
        message += f" Current next action: {next_action}"

    emit(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": message,
            }
        }
    )


if __name__ == "__main__":
    main()
