# Progressive state contract

Create a target project's root `.loopseed.md` only when at least one condition is true:

- work must continue in another task or session;
- a helper needs durable integration state;
- trusted hooks or scheduled recovery need a state signal;
- a recoverable external wait needs a relay.

Do not create it for simple single-task, read-only, docs-only, audit-only, no-write, or excluded-path work.

Use this bounded structure:

````markdown
# LoopSeed State

```loopseed-state
version=0.2.0
status=ACTIVE
next=one concise, verifiable next action
```

## Root goal

<sanitized goal>

## Plan authority

- <named plan, milestone, specification, or user instruction>

## Acceptance

- <observable condition>
- <observable condition>

## Latest direct evidence

- <at most three short evidence summaries>

## Current route

<current approach and why it is still worth trying>

## True blocker

None
````

Allowed statuses:

- `ACTIVE` — acceptance is not yet verified and a useful route remains;
- `VERIFIED` — every acceptance condition has direct evidence;
- `BLOCKED` — an exact irreplaceable permission, input, authority decision, or irreversible-risk gate exists;
- `ABORTED` — the owner explicitly stopped the run.

Rules:

1. `status=VERIFIED` is allowed only after direct acceptance evidence.
2. `status=BLOCKED` requires the exact missing item and exact unblock condition in **True blocker**.
3. Failure, poor quality, uncertainty, or a failed route keep the state `ACTIVE`.
4. Update only after new evidence, a changed route, a changed blocker, or a terminal result.
5. Replace stale evidence instead of appending history.
6. Keep `next` to one safe line; never place secrets, credentials, private absolute paths, customer data, proprietary excerpts, or chain of thought in the file.
7. A state value is a control signal, never proof.

The bundled hooks look only for this project-root file and act only when `status=ACTIVE`. The Stop hook requests at most one continuation per turn; Goal mode or a separately configured scheduled task provides durable continuation beyond that fuse.
