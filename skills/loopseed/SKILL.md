---
name: loopseed
description: Run a plan-bound, exploration-driven Codex loop from a minimal user goal. Use only when the user explicitly invokes `$loopseed` and wants autonomous progress until direct evidence verifies completion or an exact true blocker.
---

# LoopSeed

Use only for an explicit `$loopseed <goal>` invocation. Treat the remaining natural language as the root goal. If no goal is present, ask for only that goal.

Bind one root goal and observable acceptance to this authority order:

1. the user's explicit current instruction;
2. project plans, milestones, product specifications, or reference files the user names;
3. repository instructions such as `AGENTS.md`;
4. tests and the running product as evidence.

The current implementation is evidence, not authority when it conflicts with the plan.

Perform a lightweight activation handshake before substantial work: identify the planning authority, the closest real verifier, and which Codex mechanisms are actually exposed in the current surface. Select the lowest runtime level that can close the goal, verify that any selected mechanism is genuinely active, and degrade to the main-thread loop when it is unavailable. Do not spend the task building orchestration for its own sake.

Run the smallest useful loop:

1. **Explore:** inspect the closest real project state, identify the most important unknown or gap, and compare materially different routes when needed.
2. **Act:** take the highest-value reversible action available with current tools and authority.
3. **Observe:** run the affected path and collect direct output, tests, UI, screenshots, artifacts, or other real evidence.
4. **Verify:** compare evidence with the same acceptance conditions.
5. **Adapt:** if not verified, repair the cause or change route; do not repeat an unchanged failed attempt.

Default to one main thread and one writer. Load [playbook.md](references/playbook.md) only when uncertainty, independent review, delegation, or recovery materially helps. Delegate only independent work whose expected benefit exceeds coordination and token cost; prefer read-heavy exploration, tests, triage, and review. Keep integration central, and isolate parallel writers with worktrees when available.

Use Codex mechanisms progressively, not ceremonially. Attempt to activate the smallest useful native mechanism when the current surface exposes it, then verify activation from the surface or its direct behavior. Never claim Goal mode, subagents, hooks, worktrees, scheduled tasks, or permissions are active unless confirmed. If the invocation is already inside Goal mode, treat the goal text as both the objective and completion criteria. Use scheduled recovery only when work must wake later or poll an external event; do not add fixed-interval heartbeats while the active loop is making progress.

Create a project-root `.loopseed.md` only when work must survive the current task/session, a helper needs integration state, or trusted hooks/scheduled recovery will use it. Then read [state-contract.md](references/state-contract.md) and [runtime-ladder.md](references/runtime-ladder.md). The state label is never completion evidence.

Valid terminal states are only:

- `VERIFIED`: every acceptance condition has direct evidence;
- `BLOCKED`: an exact irreplaceable permission, input, authority decision, or irreversible-risk gate prevents progress;
- `ABORTED`: the owner explicitly stops the run.

Failure, low quality, an ugly interface, a failing test, uncertainty, or an exhausted first route are not blockers; explore and reroute.

Report only the outcome, direct evidence, changed scope, remaining risk, and exact unblock condition when blocked. An ordinary `$loopseed` run does not authorize modifying LoopSeed itself.
