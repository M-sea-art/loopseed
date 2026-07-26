# Changelog

## 0.3.0

- Added explicit `$loopseed one-shotted <goal>` autonomous completion mode.
- Defined One-Shotted as one human authorization rather than one model response.
- Added a dependency-free project-local control plane with goal, architecture, acceptance, expert, state, evidence, defect, and final-report contracts.
- Added the `BIND → PLAN → IMPLEMENT → VERIFY ↔ REPAIR → FINALIZE` state machine.
- Enforced independent gate verification: implementation owners cannot approve their own work.
- Made gate failure enter `REPAIR` and required verifier-authored evidence before PASS.
- Added fail-closed finalization, mandatory required gates, and P0/P1 defect blocking.
- Added two-round no-progress detection that forces root-cause replanning and a materially different route.
- Extended lifecycle hooks to resume One-Shotted state while preserving legacy `.loopseed.md` behavior.
- Added JSON schemas, reusable templates, CLI tests, hook compatibility tests, and CI validation.

## 0.2.0

- Reframed LoopSeed as a minimal natural-language activation protocol for plan-bound, exploration-driven Codex loops.
- Made single-thread execution the default and progressive escalation the efficiency rule.
- Added explicit Goal mode invocation guidance without pretending unavailable mechanisms are active.
- Added a mechanism ladder for subagents, worktrees, state relay, hooks, and scheduled recovery.
- Added a bounded `.loopseed.md` state contract with strict terminal-state semantics.
- Added optional trusted `SessionStart` and one-shot `Stop` hooks scoped to active LoopSeed state.
- Added standard-library tests and CI validation.
- Added Chinese documentation.

## 0.1.0

- Initial explicit goal-driven skill with exploration, delegation, verification, and progressive state.
