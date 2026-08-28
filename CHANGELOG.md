# Changelog

## 0.8.1

- Made game-quality criticism motion-aware: still-image superiority cannot prove animation, camera motion, battle readability, interaction, timing, feedback, or game-feel superiority when those surfaces materially depend on motion.
- Tightened the fresh Critic contract to prefer first-hand runtime observation: launch/play/operate/view the real candidate, capture critic-owned screenshots/clips/measurements, and disclose runtime-access limits instead of inheriting builder interpretation.
- Added Asset-in-Product discipline: generated or imported sprites, models, animations, materials, and effects may pass isolated sanity checks, but final product-quality PASS must come from the integrated scene when camera, scale, lighting, UI, animation, or runtime state materially affects the result.
- Added whole-product re-globalization after major Fan-out waves: integrate local winners, send one fresh critic across the complete product, find the single largest cross-surface inconsistency, and repair it before another major parallel wave.
- Added explicit Bar kinds: `Real Bar`, `Synthetic Bar`, and `Hybrid Bar`. When no meaningful real-world complement exists, the Lead may generate or construct an inspectable target and freeze it as a Synthetic Bar.
- Prevented Synthetic Bar goalpost drift: freeze before judging the corresponding candidate generation; rebind only under explicit product-authority change. A synthetic visual Bar cannot substitute for behavioral, interaction, or performance evidence.
- Updated the Seed Kernel instructions, Critic policy, plugin prompt, and Chinese production truth page without adding new schema, approval layers, or agent bureaucracy.
- Bumped One-Shotted runtime and plugin metadata to 0.8.1 and added regression coverage for the new kernel invariants.

## 0.8.0

- Restored Gauntlet as the non-overridable Seed Kernel: Goal → inspectable Bar → agent-owned decomposition → real output → fresh Critic → single biggest gap → bounded repair → ratchet.
- Split product-quality authority from runtime governance: **Gate is the floor; Bar is the ceiling.** Hard engineering/stage gates can no longer substitute for product-quality proof.
- Added first-class gate roles: `hard` and `bar`, plus CLI `add-gate --bar`.
- Made v0.8 `VERIFIED` require at least one required hard-floor gate and at least one required quality-bar gate, with all required gates backed by current bound evidence.
- Extended terminal reports with `hard_gates` and `quality_bar_gates` while preserving v0.7 receipt compatibility.
- Added status visibility for gate-role counts and current quality-bar state.
- Reframed creative dialogue as a material-ambiguity tool rather than the default center of the workflow; clear projects can go directly from Goal + Bar into production.
- Kept project context recovery, artifact/commit integrity, task ownership, no-idle scheduling, evidence ledgers, repair, and resume as the Runtime Shell supporting the kernel.
- Tightened Critic policy around real-output inspection, blind/equivalent comparison, one largest material gap, rollback of losing challengers, mirrored-order `INCONCLUSIVE`, and no silent bar softening.
- Preserved novelty protection: the Bar governs craft quality but cannot erase a load-bearing user concept merely to resemble the reference.
- Preserved bounded stop discipline: budget exhaustion, missing evidence, and no-progress are honest non-PASS outcomes; two materially similar no-progress rounds force root-cause replanning or structural reset.
- Updated the Chinese production usage guide and plugin metadata to v0.8.0.
- Added regression coverage proving that hard-floor PASS alone cannot finalize v0.8 and quality-bar PASS alone cannot finalize v0.8.

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
- Added Chinese documentation.

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
