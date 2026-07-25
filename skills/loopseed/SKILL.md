---
name: loopseed
description: Explicit goal-driven execution for Codex. Use only when the user invokes `$loopseed` followed by a goal and wants autonomous progress, direct verification, useful delegation, and an honest completion or blocker.
---

# LoopSeed

Use this Skill only for an explicit `$loopseed <goal>` invocation. Treat everything after `$loopseed` as the root goal. If no goal follows, ask for it and stop. Do not activate from similar wording, an old state file, or another task.

Bind the goal, derive observable acceptance from the user's words and the project, and keep both within the user's authority. Observe the closest real UI, command, test, artifact, file, or source before choosing work.

Choose the most valuable verifiable next action. Choose tools and route autonomously. Delegate two or more independent, non-conflicting tasks to native helpers; keep integration central. Make the smallest coherent authorized change, then verify the affected path directly. Continue from evidence; after failure, repair the cause or take a materially different path instead of repeating an unchanged attempt.

Use [playbook.md](references/playbook.md) only when exploration, independent challenge, delegation, or recovery would materially help. If native helpers are unavailable, continue in the main task.

Create a root `.loopseed.md` only after a helper is actually dispatched and needs integration state, work must continue in another task, or a recoverable blocker needs a relay. At that point read [state-contract.md](references/state-contract.md). Never create it for simple single-task work, read-only, docs-only, audit-only, no-write, or an excluded named path. The state file is not completion evidence.

When delegating, avoid conflicting writers and send only:

```text
GOAL: one observable result
EVIDENCE: what proves it
RETURN: change, evidence, or blocker
BOUNDARY: only when authority or write conflict requires it
```

Stop when acceptance is directly verified, a real gate blocks progress, or no valuable verifiable action remains. Report the outcome, evidence, changed scope or zero writes, and remaining risk. An ordinary `$loopseed` invocation does not authorize modifying LoopSeed itself.
