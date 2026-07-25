# LoopSeed

**A minimal natural-language seed for plan-bound, exploration-driven Codex loops.**

[简体中文](README.zh-CN.md)

LoopSeed does not try to encode an entire workflow in a giant prompt. It gives Codex a clear goal, binds it to the project's real plan, and keeps the execution loop moving through exploration, action, observation, verification, and recovery.

> **Minimal instruction. Maximum useful autonomy. Evidence decides when to stop.**

## What LoopSeed means

```text
Project plan + minimal goal
            ↓
          Explore
            ↓
           Act
            ↓
         Observe
            ↓
          Verify
            ↓
   not done → adapt / reroute / resume
            ↓
   done → stop with direct evidence
```

LoopSeed is a **goal-bounded self-sustaining loop**: it should keep producing the next useful action before acceptance is verified, then converge immediately. It is not a promise of literal infinite execution.

## Best invocation

Use Goal mode when the current Codex surface supports it:

```text
/goal $loopseed Follow the project's current plan and complete the active milestone with direct evidence.
```

A shorter natural-language example:

```text
/goal $loopseed 按项目规划完成当前里程碑，以实际运行证据验收。
```

For a normal current-task loop:

```text
$loopseed <your goal>
```

On a non-trivial run, LoopSeed performs a small activation handshake: locate the current plan, choose the closest real verifier, inspect which Codex mechanisms are actually exposed, and select the cheapest sufficient runtime level. If a mechanism cannot be confirmed, it falls back instead of pretending.

LoopSeed never claims Goal mode, hooks, subagents, worktrees, or scheduled tasks are active unless the current surface confirms them.

## Five-minute project setup

1. Keep one current planning source such as `PLAN.md`, a named milestone file, or an explicit user instruction.
2. Define observable acceptance in that plan: tests, running UI, screenshots, artifacts, or a complete user flow.
3. Start with the minimal seed above. Do not pre-create agents, worktrees, schedules, or state unless evidence shows they are needed.
4. Add `.loopseed.md` only when the run must survive a task/session or use the optional hooks.

## Core operating principles

1. **Plan-bound** — explicit user intent and current project planning are the authority; the existing implementation is evidence, not the product definition.
2. **Explore every loop** — uncertainty, failed paths, and quality gaps trigger renewed observation and alternative routes, not premature stopping.
3. **Single-thread by default** — one main thread and one integration path are cheapest and safest.
4. **Escalate progressively** — use subagents, state relay, worktrees, hooks, or schedules only when their expected value exceeds coordination cost.
5. **One completion truth** — acceptance criteria and direct evidence are shared by the main loop, reviewers, and stop logic.
6. **Event-driven first** — act on new evidence, failures, checkpoints, and external completion; use time-based polling only as a recovery fallback.
7. **Low process constraint, high outcome responsibility** — Codex chooses methods; the project plan and observable result constrain completion.

## Codex mechanism ladder

| Level | Mechanism | Use it when |
|---|---|---|
| 0 | Main-thread loop | Default for most work |
| 1 | `.loopseed.md` relay | Work must survive a session, task, or handoff |
| 2 | Subagents | Independent exploration, tests, triage, or review can run in parallel |
| 3 | Worktrees | More than one writer must experiment safely |
| 4 | Trusted lifecycle hooks | An active state needs resume context or a one-shot anti-early-stop fuse |
| 5 | Scheduled task | Work must wake later, poll an external event, or recover after the active session ends |

Do **not** turn every mechanism on for every task. The efficient pattern is one plan source, one root goal, one verifier, and one writer until evidence justifies escalation.

## Optional hooks

This plugin includes conservative, state-scoped hooks:

- `SessionStart` injects a short resume instruction only when the project root contains an active `.loopseed.md`.
- `Stop` requests one continuation when the state is still `ACTIVE`.
- If Codex reports `stop_hook_active: true`, the hook allows the turn to stop rather than creating recursive continuation.
- `VERIFIED`, `BLOCKED`, and `ABORTED` states never trigger continuation.

Plugin hooks require explicit trust review in Codex. They do not expand permissions, grant network access, or replace Goal mode or scheduled tasks.

## State and valid terminal states

LoopSeed creates `.loopseed.md` only when durable relay is useful. Valid terminal states are:

- `VERIFIED` — all acceptance conditions have direct evidence.
- `BLOCKED` — an exact, irreplaceable permission, input, authority decision, or irreversible-risk gate is missing.
- `ABORTED` — the owner explicitly stopped the run.

A failed attempt, ugly UI, incomplete design, failing test, uncertain next step, or exhausted first approach is **not** a terminal state. It is a reason to explore and reroute.

See [the state contract](skills/loopseed/references/state-contract.md) and [runtime ladder](skills/loopseed/references/runtime-ladder.md).

## Efficiency model

LoopSeed optimizes for:

- fewer repeated prompts;
- less main-thread context pollution;
- fewer unnecessary agents;
- fewer fixed-interval heartbeats;
- direct verification instead of status prose;
- bounded continuation instead of an uncontrolled resource loop.

## Repository layout

```text
.codex-plugin/plugin.json
skills/loopseed/
  SKILL.md
  agents/openai.yaml
  references/
hooks/
  hooks.json
  common.py
  session_start.py
  stop_continue.py
tests/
```

## Validate locally

```bash
python -m unittest discover -s tests -v
python -m json.tool .codex-plugin/plugin.json
python -m json.tool hooks/hooks.json
```

## Codex references

- [Long-running work and Goal mode](https://learn.chatgpt.com/codex/long-running-work)
- [Subagents](https://learn.chatgpt.com/codex/agent-configuration/subagents)
- [Hooks](https://learn.chatgpt.com/codex/hooks)
- [Scheduled tasks](https://learn.chatgpt.com/codex/automations)
- [Git worktrees](https://learn.chatgpt.com/codex/environments/git-worktrees)
- [AGENTS.md](https://learn.chatgpt.com/codex/agent-configuration/agents-md)

## License

MIT. See [LICENSE](LICENSE).
