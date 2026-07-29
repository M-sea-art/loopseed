# LOOPSEED C1 Minimal Rerun

## Decision

`C1_PASS`

The repaired runtime completed the required live sequence:

```text
real persisted artifact
→ failed verification
→ BLOCKED
→ fresh machine unblock evidence
→ VERIFY
→ fresh gate evidence
→ FINALIZE
```

No One-Shotted state file was edited manually.

## Project binding

- Repository: `M-sea-art/loopseed`
- LOOPSEED source branch: `experiment/evidence-governed-runtime-v0.5`
- Source commit: `09a279f26898e1c79a1806d5f70832d41e51dbdf`
- Test branch: `experiment/c1-minimal-rerun-2026-07-29`
- Candidate commit: `52708dfb6872ac2517fa9789aec972b73233bd01`
- Artifact: `artifacts/c1-delivery-receipt.json`
- Artifact SHA-256: `7890f8bbb5db2a13a5dd1192968242141b3ab1f3959cf3f8c76fbef61e98eb48`
- Project stage: C1 runtime preflight

## Block and recovery

The first real verification exited `1` because the independent verifier approval
file did not exist. Runtime entered `BLOCKED` as
`BLK-20260729T145011Z-aa2352bc`, bound to the remote candidate commit, project,
artifact path, and artifact hash.

Before unblocking, the live run rejected:

- resume without evidence;
- evidence for another blocker;
- evidence for another project;
- evidence for another candidate.

After the approval condition became true, the machine runner executed the verifier
and created `EV-20260729T145042Z-53ded2ce`. Resume accepted that fresh evidence and
returned to `VERIFY`. A second execution created gate evidence
`EV-20260729T145047Z-319866c2`; final validation and finalization then passed.

## Negative coverage

The current source commit's automated C1 tests additionally rejected stale evidence,
artifact drift after verification, and a hand-forged manual PASS for a
machine-required gate. The full repository suite passed `26/26` at the persisted
candidate commit.

## Delivery recovery

The first local `git push` attempt failed because the checkout had read-only HTTPS
credentials. The production files were therefore persisted through the connected
GitHub writer before this authoritative rerun. The run is bound to the resulting
remote commit `52708dfb...`, not to an unpushed local-only commit.

## Protected invariants

- `main` remained at `5a4097cd4398558714b1d9b526ab02641c45e52f`.
- The LOOPSEED source branch was not modified by the run.
- No pull request was created.
- The product artifact did not change between BLOCKED, resume, gate verification,
  and finalization.

