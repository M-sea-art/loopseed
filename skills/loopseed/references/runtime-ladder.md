# Runtime ladder

LoopSeed uses the cheapest mechanism that can still close the next verifiable gap.

| Level | Mechanism | Trigger | Cost control |
|---|---|---|---|
| 0 | Main-thread loop | Default | One goal, one writer, direct evidence |
| 1 | `.loopseed.md` | Cross-session/task relay is actually needed | Replace stale state; do not append a diary |
| 2 | Subagents | Work is independent and parallelizable | Prefer read-heavy tasks; return distilled results |
| 3 | Worktrees | Multiple writers need isolated experiments | Integrate centrally; do not edit the same files concurrently |
| 4 | Trusted hooks | Active state needs resume or anti-early-stop behavior | State-scoped; one Stop continuation per turn |
| 5 | Scheduled recovery | Work must wake later or poll an external event | Event-driven first; use the lowest useful cadence |

## Activation handshake

At the start of a non-trivial run, answer internally from direct project and surface evidence:

1. **Plan:** Which current document or instruction defines the milestone?
2. **Verifier:** What observable result can decide completion?
3. **Runtime:** Which native mechanisms are actually available here?
4. **Minimum:** What is the cheapest level that can close the next gap?
5. **Proof:** How will activation and progress be observed?

If a mechanism cannot be confirmed, fall back one level. Never replace unavailable runtime support with prose claiming it exists.

## Invariants

- One project-planning authority.
- One root goal.
- One acceptance definition.
- One main integration owner.
- One direct evidence trail.
- No mechanism is assumed active without confirmation.
- No fixed heartbeat while the active loop is progressing.
- No parallel writers without isolation.
- No continuation after `VERIFIED`, `BLOCKED`, or `ABORTED`.

## Recommended Goal-mode seed

```text
/goal $loopseed 按项目规划完成当前里程碑，以实际运行证据验收。
```

## Recommended scheduled recovery seed

Use only on a surface that exposes Scheduled tasks:

```text
$loopseed Resume the project-root .loopseed.md. If status is ACTIVE, inspect new evidence and execute the next verifiable action. If VERIFIED, BLOCKED, or ABORTED, do not continue. Report only meaningful state changes.
```

A schedule is a wake-up fallback, not a second main loop. Pause or remove it after a terminal state.
