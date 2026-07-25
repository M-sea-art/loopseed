# Progressive state contract

Create a target project's root `.loopseed.md` only after at least one escalation has actually occurred:

- a native helper was dispatched and needs integration state;
- work must continue in another Codex task;
- a recoverable blocker needs a durable relay.

Do not create it merely because product writes are allowed. Never create it for simple single-task work, read-only, docs-only, audit-only, no-write, or a named-path-only request that excludes it.

Use this bounded structure:

```markdown
# LoopSeed State

- version: 0.1.0
- status: ACTIVE

## Root goal and acceptance

<sanitized goal and observable completion conditions>

## Recent direct evidence

- <at most three short evidence summaries>

## Next gap or blocker

<one next verifiable result or exact recoverable blocker>
```

Allowed statuses are `ACTIVE`, `VERIFIED`, `BLOCKED`, and `RELAY_REQUIRED`.

Redact credentials, usernames, private absolute paths, customer data, proprietary excerpts, and chain of thought. Replace stale evidence instead of appending history. Update the file only after a verified milestone, changed blocker, relay decision, or terminal result. A state label never substitutes for direct acceptance evidence.
