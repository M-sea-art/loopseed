# Changelog

## 0.7.1

- Restored the C1.1 machine-evidence core without replacing v0.7 creative calibration or scheduling.
- Added real verifier command execution with preserved shell input, exit code, timeout, bounded output, Git HEAD, tracked/untracked candidate cleanliness, and artifact SHA-256 receipts.
- Added generation- and ledger-boundary-aware verification bindings so repaired candidates invalidate stale gate passes without timestamp races.
- Required human and visual PASS evidence to reference existing, hashed project artifacts.
- Required every `required:true` task to finish as `SUCCEEDED` and every optional task to receive an explicit terminal disposition before finalization.
- Added schema-backed, cross-ledger final-report validation with rollback on failed terminal writes.
- Added short transactional state locks and parallel verifier activity coordination so concurrent gate receipts merge without blocking task updates.
- Added ACTIVE v0.7 migration: legacy command claims become machine gates, pre-binding PASS references reset, cancelled legacy candidate arms can be marked optional, and locked creative briefs remain resumable.
- Classified terminal v0.7 receipts as legacy/unattested rather than silently re-signing them.
- Added deterministic attacks for false commands, timeouts, missing/drifting/symlinked artifacts, dirty or untracked candidate inputs, wrong HEAD, forged/orphaned evidence, unsettled tasks, concurrency, version downgrade, and terminal-report tampering.

## 0.7.0

- Added a dependency-free `task-graph.json` runtime for bounded One-Shotted Fan-out.
- Classified task relations as `HARD_DEPENDENCY`, `SOFT_ADVICE`, or `INDEPENDENT`.
- Added explicit `ALL_REQUIRED`, `FIRST_SUCCESS`, and `QUORUM` joins.
- Added safe runnable-batch scheduling with capacity and write-isolation checks.
- Added `NO_IDLE_WHILE_RUNNABLE`: a wait is rejected while safe work remains.
- Added task-level status, legal-wait recording, global BLOCKED protection, audit coverage, and regression tests.

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
