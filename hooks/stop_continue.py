"""Request one continuation when active LoopSeed acceptance is not verified."""

from __future__ import annotations

from common import compact, emit, load_state, read_event, state_status


def main() -> None:
    event = read_event()
    _, state = load_state(event.get("cwd"))

    if state_status(state) != "ACTIVE":
        return

    # Codex marks a continuation turn so a Stop hook can avoid recursive loops.
    if event.get("stop_hook_active") is True:
        return

    next_action = compact(state.get("next"))
    reason = (
        "LoopSeed remains ACTIVE. Read the project-root .loopseed.md and continue "
        "from its latest direct evidence. Before stopping, either produce new "
        "evidence and update the next action, mark VERIFIED only when every "
        "acceptance condition is directly satisfied, or mark BLOCKED only for an "
        "exact irreplaceable permission, input, authority decision, or "
        "irreversible-risk gate. If the last route failed, explore a materially "
        "different route instead of repeating it."
    )
    if next_action:
        reason += f" Next verifiable action: {next_action}"

    emit({"decision": "block", "reason": reason})


if __name__ == "__main__":
    main()
