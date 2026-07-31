# LoopSeed Version Management

## Version strategy

LoopSeed keeps `main` as the released stable baseline. Experimental branches represent one explicit hypothesis and must not silently replace earlier contracts.

## Current version map

| Version | Branch / State | Purpose | Status |
|---|---|---|---|
| v0.1 | initial source | Plugin foundation | archived baseline |
| v0.2 | main history | Project-agnostic autonomous loop, runtime escalation, state relay | completed |
| v0.3 | `main` | One-Shotted planning, verification, repair, fail-closed finalization | released stable baseline |
| v0.4.x | design/protocol evolution | Improvement units, coupling awareness, Fresh Critic, merge discipline | protocol reference |
| C0 | v0.5 experiment history | Binding and evidence protocol overlay maintained as documents | rejected for promotion |
| C1 | v0.5 experiment history | Executable resume and machine evidence | minimal runtime PASS; cross-project binding defect found |
| C1.1 | `experiment/c1.1-binding-integrity-repair-2026-07-30` | Explicit binding and integrity-stable evidence transaction | experimental repair candidate |

## Branch rules

- `main`: stable release baseline only.
- `experiment/*`: isolated validation and implementation branches.
- Every experiment documents its inherited commit, changed contract, expected improvement, verification method, and rollback condition.
- Failed runs remain immutable evidence; repair uses new commits and a fresh run.
- No PR to `main` before the current candidate passes its declared cross-project gate.

## C1.1 promised scope

C1.1 intentionally stays narrow:

1. explicit project/candidate/artifact binding before machine verification;
2. actual Git HEAD verification when Git is present;
3. command-executed gate and unblock evidence;
4. expected/before/after artifact identity equality;
5. resumable `BLOCKED -> ACTIVE / VERIFY` with fresh stable evidence;
6. independent audit and fail-closed finalization;
7. synchronized tests, schemas, documentation, and prerelease versioning.

## Deferred scope

The following ideas remain research or later candidates and are not claimed by C1.1:

- Production Frontier or champion/challenger state;
- a multi-dimensional Strong Verdict model;
- full worktree or filesystem attestation;
- immutable verification sandboxes;
- multi-artifact manifests;
- new permanent agent roles or production phases.

They should be added only after a real failure proves that the C1.1 subject model is insufficient.

## Promotion rule

C1.1 may be reviewed for experimental Runtime promotion only after:

```yaml
runtime:
  explicit_binding: PASS
  actual_head_binding: PASS
  mutation_during_verification_rejected: PASS
  gate_and_unblock_integrity: PASS
  regression_suite: PASS
cross_project:
  fresh_blocked_resume_verify_finalize: PASS
  fresh_verifier_open_p0_p1: 0
repository:
  main_unchanged: true
  docs_schemas_tests_aligned: true
```

Until then, v0.3 remains the released core.
