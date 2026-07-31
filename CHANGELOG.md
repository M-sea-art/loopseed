# Changelog

## 0.3.1-c1.1 — experimental

- Fixed repeat initialization so it returns a controlled error without mutating the existing run; `--force` remains the explicit replacement path.
- Made finalization preflight the committed final-report schema, cross-check the receipt against state, gates, evidence, goal, and binding, and roll back terminal files if final validation fails.
- Rejected artifacts outside the declared project root, closing the repository-A plus artifact-B binding gap.
- Added explicit `bind` for one project, candidate commit, and artifact before machine verification.
- Made identical binding idempotent and rejected silent subject replacement.
- Added independent actual Git `HEAD` verification when the target is a real worktree; dirty state is recorded but not automatically rejected.
- Upgraded `run-evidence` into an integrity transaction: PASS requires exit code `0` and identical expected, before-command, and after-command artifact identities.
- Made verifier-time artifact mutation or deletion produce machine FAIL for both gate and unblock evidence.
- Made audit, resume, and finalization independently reject unstable, forged, stale, or wrongly bound machine evidence.
- Preserved evidence-bound `BLOCKED -> ACTIVE / VERIFY` recovery.
- Added schemas for C1.1 state, machine evidence, machine gates, and final reports.
- Added focused tests for explicit binding, mutation during gate and unblock commands, forged subject hashes, actual Git HEAD mismatch, and CLI dispatch.
- Updated English and Chinese documentation to match the executable Runtime.

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
