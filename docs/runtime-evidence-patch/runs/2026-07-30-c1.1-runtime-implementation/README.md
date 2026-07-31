# LOOPSEED C1.1 Runtime implementation — 2026-07-30

## Decision

`C1_1_RUNTIME_IMPLEMENTED — AWAITING_FRESH_CROSS_PROJECT_RERUN`

This run implements the narrow binding-integrity repair required after the real
cross-project `C1_BINDING_FAILED` result. It does not promote C1.1 to `main` and
does not reinterpret the failed product run as complete.

## Source and isolation

- Repository: `M-sea-art/loopseed`
- Released core: `main` at `5a4097cd4398558714b1d9b526ab02641c45e52f`
- C1 baseline: `experiment/evidence-governed-runtime-v0.5` at
  `09a279f26898e1c79a1806d5f70832d41e51dbdf`
- Repair branch: `experiment/c1.1-binding-integrity-repair-2026-07-30`
- Review and repair contract base: `3ca526616480f2869d27bc460b2236be17a9b5d1`
- Runtime code checkpoint: `f94cee8f605986f026a10d6dd01d250ade3aed4d`
- Repair contract implementation checkpoint:
  `1fafb6ba0410f70a7a7bde390b510fc16a3814b8`

`main` was not modified and no pull request was created by this implementation
run.

## Implemented capability

### Explicit binding

C1.1 adds a public `bind` command that fixes one verification subject before
machine evidence is accepted:

```text
project ID
+ candidate commit
+ artifact path
+ artifact SHA-256
```

When the target is a real Git worktree, the Runtime independently verifies
`git rev-parse HEAD`. An identical binding is idempotent. A different project,
candidate, artifact path, or artifact hash requires a fresh run rather than a
silent rebind.

### Integrity-transaction evidence

`run-evidence` now derives PASS from both command success and subject stability:

```text
exit code == 0
AND actual Git HEAD == bound candidate (when Git is present)
AND expected artifact == artifact before == artifact after
```

A verifier command that modifies or deletes the artifact records machine FAIL.
The same rule applies to gate and unblock evidence.

### Independent enforcement

The runner, audit, resume, and finalizer no longer trust one another's prose or
`result` field alone:

- audit recomputes expected/before/after consistency;
- audit checks current Git HEAD and current artifact identity;
- resume accepts only fresh, integrity-stable machine evidence for the active
  blocker;
- machine gate evidence produced before the latest resume cannot finalize;
- final reports include the verified binding.

### Contract alignment

The executable Runtime, tests, schemas, templates, plugin prerelease version,
English and Chinese README, skill instructions, One-Shotted reference, state
contract, changelog, and version-management document were aligned to the same
C1.1 promise.

Production Frontier, full Strong Verdict, full worktree attestation, immutable
sandboxes, and multi-artifact manifests remain explicitly deferred.

## Verification

The execution container could not clone GitHub directly, so the branch was
verified in an isolated local tree reconstructed from connector-fetched remote
contents. This is not presented as a GitHub Actions result.

Observed isolated regression result:

- Original One-Shotted tests: PASS
- Existing lifecycle-hook tests: PASS
- C1 CLI tests: PASS
- C1/C1.1 Runtime tests: PASS
- Total: **33 passed, 0 failed**

Focused C1.1 coverage includes:

- machine gate execution without first entering `BLOCKED`;
- idempotent explicit binding and silent rebind rejection;
- verifier-time artifact mutation with exit code zero;
- unblock-command artifact mutation;
- forged PASS with mismatched subject hashes;
- actual Git HEAD mismatch;
- legacy `BLOCKED -> fresh evidence -> VERIFY -> FINALIZE` recovery;
- original LoopSeed and hook behavior.

A GitHub workflow was added at `.github/workflows/c1.1-runtime-ci.yml`, but no
remote workflow success is claimed in this receipt because no verifiable commit
status was available through the current connector response.

## Current boundary

C1.1 is now an implemented experimental Runtime candidate, not a released core.
The next allowed promotion evidence is one fresh real cross-project run using:

- a new product candidate commit;
- the C1.1 Runtime branch;
- a fresh blocker and unblock event;
- fresh machine gate evidence;
- no manual state edit;
- a Fresh Verifier with zero open P0/P1 defects.

A/B groups are not rerun. The previously failed cross-project run remains
immutable evidence.
