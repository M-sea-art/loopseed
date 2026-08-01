# LoopSeed state contracts

LoopSeed keeps state only when durable relay is useful. State is a control signal, never proof.

## Standard mode

Use project-root `.loopseed.md` only when work must survive a task/session, a helper needs integration state, trusted hooks will resume it, or an external wait needs a relay.

````markdown
# LoopSeed State

```loopseed-state
version=0.7.0
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

One-Shotted mode uses `.loopseed/one-shotted/` and the bundled CLI rather than `.loopseed.md`.

Its state is split into:

- `goal-contract.json` — root seed, domain, production mode, calibration state, and completion policy;
- `creative-brief.json` — draft or locked product authority;
- `compiled-shot.md` — human-readable production brief generated only after lock;
- `dialogue.jsonl` — compact append-only creative decisions and option turns;
- `acceptance.json` — gates, owners, independent verifiers, and evidence references;
- `state.json` — current phase, status, production round, dialogue rounds, and next action;
- `expert-registry.json` — integration, verification, creative, and mode-aware Fan-out responsibilities;
- `task-graph.json` — bounded tasks, dependency kinds, join policies, write isolation, and current task status;
- `evidence.jsonl` — append-only verifier verdicts;
- `defects.jsonl` — append-only defect status events;
- `final-report.json` — generated only by the finalizer.

The One-Shotted JSON state takes precedence over legacy `.loopseed.md` for bundled hooks.

`state.json.scheduler_wait` is normally `null`. A non-null wait is valid only when the scheduler reports no safe runnable task, every named wait target is already `RUNNING`, the reason is `HARD_DEPENDENCY` or `JOIN`, and a fallback is recorded. It is a control signal, not permission to mark the project `BLOCKED`.

## Phases

```text
CALIBRATE → BIND → PLAN → IMPLEMENT → VERIFY → REPAIR / FINALIZE
```

### CALIBRATE

Used by default for game goals and optionally for general or Moonshot projects.

While open:

- the model records compact synthesis, questions, options, and advanced decision surfaces;
- the user records answers or decisions;
- each model question advances the product and offers two to four options with one recommendation;
- no production acceptance gate may be added;
- no ordinary transition may leave the phase;
- no production file should be written under the authority of an unlocked brief.

Only `lock-brief` may move `CALIBRATE → BIND`.

### BIND and later

The locked creative brief compiles into project, artifact, and stage authority. Production then follows the ordinary One-Shotted state machine.

## Calibration state

`goal-contract.json.calibration` contains:

```json
{
  "enabled": true,
  "status": "OPEN",
  "policy": "game-first-creative-co-director",
  "max_rounds": 5,
  "dialogue_rounds": 0,
  "brief_id": null,
  "locked_at": null
}
```

Allowed states:

- `OPEN` — phase must remain `CALIBRATE` while ACTIVE;
- `LOCKED` — `creative-brief.json`, `compiled-shot.md`, user authorization, and matching brief ID are required;
- `SKIPPED` — direct route; phase may begin at `BIND`.

The configured dialogue maximum is one to eight model question rounds. It is a ceiling, not a quota. `state.json.dialogue_rounds`, the goal contract, and the dialogue ledger must agree after lock.

## Dialogue ledger

Each `dialogue.jsonl` event contains:

- unique ID and run ID;
- actor: `user` or `model`;
- kind: `seed`, `synthesis`, `question`, `answer`, or `decision`;
- round number;
- compact summary;
- model effects such as preserve, correct, amplify, complete, or continue;
- material decision surfaces advanced;
- two to four options plus a recommendation for model questions;
- timestamp.

The ledger stores decisions, not full transcripts, secrets, or private reasoning.

## Creative lock

A locked `creative-brief.json` must reference:

- at least one model synthesis or question event;
- at least one user event;
- a user `answer` or `decision` as the authorization event.

For games it must also contain the complete game contract, including player promise, core loop, world response, unique hook, art direction, game feel, hero moment, vertical slice, asset strategy, and performance budget.

Moonshot additionally requires an ambition expansion, scope guard, and explicit amplification.

## Invariants

1. Use the CLI for dialogue, lock, PASS, FAIL, defect, transition, and finalization events.
2. Do not write `VERIFIED` manually.
3. Do not make an implementation owner its own verifier.
4. Do not create production gates before the creative lock when dialogue is enabled.
5. Do not bypass `CALIBRATE` with a hand-edited phase change.
6. Keep `next_action` to one safe line.
7. Accepted dialogue decisions accumulate; later rounds may not silently reset them.
8. Every model question has two to four meaningful options and one recommendation.
9. Never store credentials, private absolute paths, customer data, proprietary excerpts, or chain of thought.
10. Stop hooks request at most one continuation per turn and never continue after `VERIFIED`, `BLOCKED`, or `ABORTED`.
11. Do not wait while `task-graph.json` contains a safe runnable task.
12. Treat `SOFT_ADVICE` as non-blocking and `BLOCKED` as external-only.
