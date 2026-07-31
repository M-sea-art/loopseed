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

## Production usage guide synchronization gate

`docs/usage-guide.zh-CN.md` is the canonical living guide for choosing Standard vs One-Shotted mode, selecting the current production branch, writing compact goals, applying evidence gates, and controlling Critic/Fan-out cost.

Every version upgrade must update the guide in the same change. An upgrade includes any change to:

- `.codex-plugin/plugin.json` version;
- user-visible commands or invocation syntax;
- Standard or One-Shotted behavior;
- project binding, Gate, evidence, state, BLOCKED/Resume, or finalization rules;
- the recommended stable or experimental production route;
- default cost, Critic, Fan-out, or verification policy;
- examples that no longer represent the latest recommended practice.

The upgrade is documentation-incomplete until all of the following are true:

```yaml
usage_guide:
  loopseed_version_matches_plugin: true
  last_updated_refreshed: true
  commands_and_examples_current: true
  version_map_current: true
  production_route_current: true
  cost_policy_current: true
  verifier_passed: true
```

Required check:

```bash
python tools/verify_usage_guide_version.py
```

CI must fail closed when the version declared by `docs/usage-guide.zh-CN.md` differs from `.codex-plugin/plugin.json`. A version bump without a synchronized guide update must not be described as a complete upgrade.

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
  usage_guide_version_check: PASS
```

Until then, v0.3 remains the released core.
