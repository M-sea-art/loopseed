# Runtime ladder

LoopSeed uses the cheapest mechanism that can still close the next verifiable gap.

Creative dialogue and production runtime are separate decisions:

- dialogue increases precision before production;
- the runtime ladder increases execution power after the shot is locked.

| Level | Mechanism | Trigger | Cost control |
|---|---|---|---|
| 0 | Main-thread loop | Default | One goal, one writer, direct evidence |
| 1 | `.loopseed.md` or One-Shotted control state | Cross-session/task relay is actually needed | Replace stale state; do not append a diary |
| 2 | Subagents | Work is independent and parallelizable | Inherit one creative brief and integrity refs; return distilled results |
| 3 | Worktrees | Multiple writers need isolated experiments | Integrate centrally; do not edit the same files concurrently |
| 4 | Trusted hooks | Active state needs resume or anti-early-stop behavior | State-scoped; one Stop continuation per turn |
| 5 | Scheduled recovery | Work must wake later or poll an external event | Event-driven first; use the lowest useful cadence |

## Preproduction gate

Before activating production helpers for a calibrated run:

1. creative dialogue is `LOCKED`;
2. the user authorization event is recorded;
3. `creative-brief.json` and `compiled-shot.md` exist;
4. production mode is `focused`, `studio`, or `moonshot`;
5. Project Binding, Artifact Contract, and Stage Target can be frozen from the shot.

No runtime escalation may be used to bypass an unresolved product direction.

## Activation handshake

At the start of non-trivial production, answer internally from direct project and surface evidence:

1. **Shot:** Which locked creative brief or direct contract defines the result?
2. **Mode:** Is this Focused, Studio, or Moonshot?
3. **Plan:** Which current document or instruction defines the milestone?
4. **Verifier:** What observable result can decide completion?
5. **Runtime:** Which native mechanisms are actually available here?
6. **Independence:** Which units can be judged and merged independently?
7. **Minimum:** What is the cheapest level that can close the next gap at the selected mode?
8. **Proof:** How will activation and progress be observed?

If a mechanism cannot be confirmed, fall back one level. Never replace unavailable runtime support with prose claiming it exists.

## Mode-aware escalation

### Focused

- remain at Level 0 unless one independent gap justifies a helper;
- prefer one lead and one verifier;
- do not increase scope because parallel capacity exists.

### Studio

- use specialists only for production disciplines required by the vertical slice;
- parallelize isolated assets, audio, tests, bounded UI, or profiling when profitable;
- require whole-product merge, playtest, visual review, and performance verification.

### Moonshot

- use the strongest available runtime for genuinely independent quality surfaces;
- isolate parallel writers;
- allow contract-identical candidates and harsh independent criticism;
- retain one integration owner and the locked scope guard;
- never lower acceptance because the runtime is expensive or unavailable.

## Invariants

- One user-authorized creative shot when calibration is enabled.
- One project-planning authority.
- One root goal.
- One acceptance definition.
- One main integration owner.
- One direct evidence trail.
- No mechanism is assumed active without confirmation.
- No fixed heartbeat while the active loop is progressing.
- No parallel writers without isolation.
- No Fan-out before the creative and integrity locks.
- No continuation after `VERIFIED`, `BLOCKED`, or `ABORTED`.

## Recommended game seed

```text
$loopseed one-shotted 帮我通过有意义的选项校准并放大这个游戏设想；创意简报锁定后，按选定档位一次性生产、整合、试玩并以证据验收。
```

## Recommended general Goal-mode seed

```text
/goal $loopseed 按项目规划完成当前里程碑，以实际运行证据验收。
```

## Recommended scheduled recovery seed

Use only on a surface that exposes Scheduled tasks:

```text
$loopseed Resume the project-root LoopSeed state. If status is ACTIVE, inspect new evidence and execute the next verifiable action. If VERIFIED, BLOCKED, or ABORTED, do not continue. Report only meaningful state changes.
```

A schedule is a wake-up fallback, not a second main loop. Pause or remove it after a terminal state.
