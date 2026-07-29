# C1 runtime implementation — 2026-07-29

## Result

`C1_RUNTIME_IMPLEMENTED — READY_FOR_MINIMAL_RERUN`

This implementation addresses the exact preflight failure recorded at
`f3ad529be4da5732684e0216eb61ebb854e7a22f` without modifying `main` or opening a
pull request.

## Source and branch

- Released core remains: `main` at LoopSeed v0.3.0
- Evidence-governed baseline: `9d77d0b3d4c32c3c5ab98df82977f3fc4e8af4da`
- Implementation branch: `experiment/c1-runtime-implementation-2026-07-29`
- Preflight evidence is retained in the branch history.

## Implemented capability

1. Added `resume`, restricted to `BLOCKED -> ACTIVE/VERIFY`.
2. Resume requires fresh machine evidence produced after the active blocker.
3. Added `run-evidence`, which actually executes a command and records:
   - exit code;
   - bounded stdout/stderr;
   - start/finish timestamps;
   - project ID;
   - candidate commit;
   - artifact path and SHA-256;
   - gate or blocker identity;
   - actor and machine producer identity.
4. Added C1 blocker binding for project, candidate and artifact identity.
5. Added `add-gate --machine`; a manual `record PASS` cannot satisfy such a gate.
6. Final validation rejects machine gate evidence after artifact drift.
7. Timestamp precision was increased so freshness can be decided without a
   same-second ambiguity.

## Rejection coverage

Automated tests reject:

- absent resume evidence;
- stale resume evidence;
- wrong blocker evidence;
- wrong project binding;
- artifact drift after verification;
- hand-forged manual PASS for a machine-required gate.

A separate CLI regression test protects against the discovered argparse bug
where `run-evidence --command` initially shadowed the subcommand name.

## Verification

Because the execution container could not resolve `github.com`, the repository
could not be cloned directly. Verification used an isolated local test tree
reconstructed from GitHub connector-fetched branch contents. No unverified CI
claim is made.

Observed results:

- Original One-Shotted tests: **11 passed**
- Existing lifecycle-hook tests: **7 passed**
- New C1 runtime tests: **7 passed**
- New C1 CLI dispatch test: **1 passed**
- Total: **26 passed**
- CLI smoke completed:
  `BLOCKED -> machine UNBLOCK evidence -> resume -> machine gate evidence -> VERIFIED`

## Scope boundary

This is a C1 runtime implementation and preflight verification, not product
promotion and not a v0.5 core promotion. The next allowed action is to rerun
only the minimal C1 task. T2/T3 and real product work remain blocked until that
rerun confirms the runtime on an actual checkout without manual state edits.
