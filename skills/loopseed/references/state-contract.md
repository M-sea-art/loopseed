# LoopSeed state contracts

LoopSeed keeps state only when durable relay is useful. State is a control signal, never proof.

## Standard mode

Use project-root `.loopseed.md` only when work must survive a task/session, a helper needs integration state, trusted hooks will resume it, or an external wait needs a relay.

````markdown
# LoopSeed State

```loopseed-state
version=0.3.0
status=ACTIVE
next=one concise, verifiable next action
```

## Root goal
<sanitized goal>

## Plan authority
- <named source>

## Acceptance
- <observable condition>

## Latest direct evidence
- <at most three compact items>

## Current route
<current approach>

## True blocker
None
````

Allowed statuses are `ACTIVE`, `VERIFIED`, `BLOCKED`, and `ABORTED`. `BLOCKED` requires the exact missing item and exact unblock condition. Replace stale evidence rather than appending a diary.

## One-Shotted mode

One-Shotted mode uses `.loopseed/one-shotted/` and the bundled CLI rather than `.loopseed.md`. Its state is split into:

- `goal-contract.json` — immutable root authorization and completion policy;
- `acceptance.json` — gates, owners, independent verifiers, and evidence references;
- `state.json` — current phase, status, round, and next action;
- `evidence.jsonl` — append-only verifier verdicts;
- `defects.jsonl` — append-only defect status events;
- `final-report.json` — generated only by the finalizer.

The One-Shotted JSON state takes precedence over legacy `.loopseed.md` for bundled hooks.

Rules:

1. Use the CLI for PASS, FAIL, defect, transition, and finalization events.
2. Do not write `VERIFIED` manually.
3. Do not make an implementation owner its own verifier.
4. Keep `next_action` to one safe line.
5. Never store credentials, private absolute paths, customer data, proprietary excerpts, or chain of thought.
6. Stop hooks request at most one continuation per turn and never continue after `VERIFIED`, `BLOCKED`, or `ABORTED`.
