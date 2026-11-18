# LoopSeed state contracts

LoopSeed keeps state only when durable relay is useful. State is a control signal, never proof.

## Vision

Use `.loopseed.md` at the project root for a vision that should survive the current session. Save it early enough that an interruption leaves useful context. Keep the user's actual authorization, what changed in the product and what is still worth finding out in ordinary prose. For example:

````markdown
# LoopSeed

```loopseed-state
version=0.9.0
mode=vision
status=ACTIVE
```

Let a first-time player find a reason to return. In the current build, banking a catch
ends the voyage and restarting repeats the same three draws. Does knowing the risks
earlier make the choice to return to port more interesting?
````

If an explicit new vision follows a terminal One-Shotted run, copy that run's `run_id` from `.loopseed/one-shotted/state.json` into the fence as `after_one_shotted=<run_id>`. An active strict run retains ownership. Naming the finished run distinguishes new authorization from a stale note.

An untracked, regular project-root vision note is control data. Writing it preserves the finished candidate's receipt. It cannot serve as a bound deliverable or evidence. Tracked edits and other untracked project files retain their usual integrity checks.

For an explicit wall-clock limit, record the absolute end in `deadline_utc` (ISO 8601 with timezone). Preserve it across resumes. The hooks suppress continuation after expiry or if the supplied deadline cannot be interpreted. Use the host's remaining allowance for a token or spending limit. Honor the current user instruction and the host Goal's stop state at every resume.

Set `ABORTED` at an owner stop. Use `BLOCKED` for an exhausted allowance or exact missing external condition and record what would permit a restart. Keep the latest observation and the reason for stopping. An interruption with authorization still active leaves the note available at the next project session. SessionStart supplies the note as context. The native Goal or equivalent running host owns continuation and its budget. The Stop hook yields for visions, so an unrelated bounded task in the same project can finish. Earlier standard notes and strict runs retain their one-continuation Stop behavior.

## Bounded tasks and earlier notes

A bounded request ends when the requested outcome has been checked. It normally needs no state file. Existing unmarked standard notes retain the following format for durable relay.

````markdown
# LoopSeed State

```loopseed-state
version=0.7.1
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
- `state.json` — current phase, status, production round, dialogue rounds, next action, and verification-binding generations;
- `expert-registry.json` — integration, verification, creative, and mode-aware Fan-out responsibilities;
- `task-graph.json` — bounded tasks, dependency kinds, join policies, write isolation, and current task status;
- `evidence.jsonl` — append-only verifier verdicts;
- `defects.jsonl` — append-only defect status events;
- `final-report.json` — generated only by the finalizer.

The hooks give active One-Shotted state precedence. A vision that explicitly names a finished run can take over from that run. Earlier unmarked notes retain the original precedence.

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

This semantic project binding is distinct from `state.json.verification_binding`. The latter is created only in `VERIFY`, after a concrete candidate is built. It freezes a generated binding ID, generation number, evidence-ledger boundary, real Git HEAD, and one project-local file or directory SHA-256. Candidate and verifier source must be committed: tracked content must match HEAD, while non-ignored untracked content must be the bound or current hashed evidence artifact. `.loopseed` remains control data; `.git`, `.loopseed`, the whole project root, external paths, and every symlinked artifact path/tree are forbidden.

If repair changes the candidate, bind again in `VERIFY`. The old receipt moves to `verification_history`, the generation increments, `evidence_ledger_count` fixes the new generation boundary without relying on timestamps, and all old gate statuses and evidence references reset to `PENDING`.

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
13. Treat commands as machine evidence only when `run-evidence` executed them successfully without timeout.
14. Require a project-local hashed screenshot, recording, or report for human or visual PASS evidence.
15. Require every `required:true` task to be `SUCCEEDED`; mark disposable candidate arms optional and explicitly `CANCELLED` when discarded.
16. Cross-check the terminal report against the current contracts, ledgers, task graph, verification binding, and verified timestamp.
