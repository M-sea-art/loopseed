# T1 cloud experiment — 2026-07-28

## Scope

This wave executed the small-game vertical-slice triplet in isolated fresh
builder sessions:

- A: vanilla autonomous one-shot
- B: LoopSeed v0.3.0 at `5a4097c`
- C0: LoopSeed v0.3.0 plus the fixed v0.5 evidence protocol overlay

C0 is `PROTOCOL_ONLY`. No executable v0.5 runner was present, so this wave is
not a C1 promotion test.

All three builders used the same frozen Chinese task, no external research,
generated images, or external assets, one writer, at most two repair rounds,
and at most three runtime captures.

## Infrastructure recovery

The generic Cloud Browser could not reach workspace `localhost`, and the
preinstalled Playwright package had no browser executable. Every builder
reported that boundary instead of fabricating runtime evidence.

The experiment lead then created one shared, internal Sites Agent Preview
harness and loaded each frozen artifact into it without changing product
source or publicly deploying it. Each cell was exercised through two complete
three-night paths and received exactly three runtime captures.

## Blind product score

The evaluator received anonymous runnable candidates and captures only. It did
not receive builder summaries, runtime labels, or arm identities.

| Arm | Anonymous candidate | Loop | Consequence | Interaction | Visual | Evidence | Total |
|---|---|---:|---:|---:|---:|---:|---:|
| B | candidate-cedar | 5 | 5 | 5 | 5 | 5 | **25/25** |
| C0 | candidate-rain | 5 | 5 | 4 | 5 | 5 | **24/25** |
| A | candidate-ember | 5 | 5 | 4 | 4 | 5 | **23/25** |

Raw blind report: [`blind-evaluation.md`](blind-evaluation.md).

## Runtime findings

### A

- Product: PASS after lead harness recovery
- Builder claim: `EVIDENCE_BLOCKED`
- False completion: no
- Evidence structure: weakest of the three, but sufficient after lead
  verification

### B

- Product: blind quality winner at 25/25
- Builder claim: `BLOCKED`
- False completion: no
- Material runtime defect: after the exact unblock condition became true, the
  frozen v0.3 CLI rejected transition, evidence recording, and finalization
  because `BLOCKED` is terminal
- Result: the product gates passed in reality, while the v0.3 control plane
  remained permanently `BLOCKED`

### C0

- Product: PASS at 24/25, one point below B
- Builder claim: `BLOCKED_EXTERNAL_VALIDATION`
- False completion: no
- Evidence improvement: explicit binding receipt, artifact hashes, evidence
  chain, Production Frontier, and separated execution/evidence/quality/terminal
  states
- Runtime limitation: these records were manually maintained protocol files;
  the underlying v0.3 control plane still remained terminally `BLOCKED`
- Result: better auditability, but no machine-enforced recovery and no product
  quality win over B

## Decision

`C1_NOT_EXECUTABLE — DO_NOT_PROMOTE_V0.5`

This wave rejects promotion, not the evidence-governed direction:

1. C0 cannot qualify for promotion by experiment rule.
2. C0 did not beat B on blind product quality.
3. C0 added protocol records but did not solve the underlying terminal-state
   recovery problem.
4. Running T2 and T3 now would spend quota on a candidate that is ineligible to
   become core.

Retain v0.3 as the released core. Before resuming the nine-cell promotion
suite, implement a C1 candidate with:

- a resumable `BLOCKED -> VERIFY` transition when the recorded unblock
  condition becomes true;
- machine-enforced Project Binding Receipt validation;
- command, exit status, artifact identity/hash, runtime capture, actor, and
  verdict records;
- machine-maintained Production Frontier and separated strong verdict fields;
- tests proving absent or stale evidence cannot finalize.

Then resume with T2 B-C1-A. T1 A/B need not be repeated; rerun only T1-C1
because the current C cell was protocol-only.
