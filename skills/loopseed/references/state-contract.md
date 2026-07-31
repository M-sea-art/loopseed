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
- `acceptance.json` — gates, owners, independent verifiers, machine requirements, and evidence references;
- `state.json` — current phase, status, binding, blocker, resume metadata, and next action;
- `evidence.jsonl` — append-only manual and machine evidence events;
- `defects.jsonl` — append-only defect status events;
- `final-report.json` — generated only by the finalizer.

The One-Shotted JSON state takes precedence over legacy `.loopseed.md` for bundled hooks.

### Binding contract

C1.1 stores one optional active binding in `state.json`:

```yaml
binding:
  project_id: PROJECT-P01
  candidate_commit: <commit>
  artifact:
    path: dist/app.js
    kind: file
    sha256: <64 hex>
  git_repository_detected: true
  actual_candidate_commit: <commit>
  worktree_dirty: false
  bound_at: <UTC timestamp>
```

Use the `bind` command to create it. Repeating the identical binding is idempotent. A different project, candidate, artifact path, or hash requires a fresh run; do not rewrite the subject in place.

### Machine evidence contract

A machine evidence event records:

```yaml
kind: MACHINE
purpose: GATE | UNBLOCK
project_id: PROJECT-P01
bound_candidate_commit: <commit>
actual_candidate_commit: <commit or null>
expected_artifact: {path, kind, sha256}
artifact_before: {path, kind, sha256}
artifact_after: {path, kind, sha256}
integrity_stable: true | false
integrity_failure_reason: null | <reason>
exit_code: 0
result: PASS | FAIL
```

For PASS, command exit must be `0`, actual Git identity must match when available, and expected/before/after artifact identities must be identical. Audit and finalization recompute these rules independently.

### BLOCKED recovery contract

`BLOCKED` allows the current session to stop, but it is not an irreversible terminal outcome. A bound blocker contains its own ID, timestamp, reason, unblock condition, and a copy of the active binding. It may return to `ACTIVE / VERIFY` only through `resume` with fresh, machine-produced, integrity-stable evidence for that exact blocker.

`VERIFIED` and `ABORTED` remain irreversible outcomes.

Rules:

1. Use the CLI for binding, PASS, FAIL, defect, transition, recovery, and finalization events.
2. Do not write `VERIFIED` or mutate a binding manually.
3. Do not make an implementation owner its own verifier.
4. A manual PASS cannot satisfy a machine-required gate.
5. Keep `next_action` to one safe line.
6. Never store credentials, private absolute paths, customer data, proprietary excerpts, or chain of thought.
7. Stop hooks request at most one continuation per turn. They allow stop in `BLOCKED`, but recovery requires explicit evidence-bound `resume`.
