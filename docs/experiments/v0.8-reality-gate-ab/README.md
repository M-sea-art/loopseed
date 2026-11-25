# v0.8 Reality Gate equal-budget A/B

Status: **experiment only**  
Baseline: `main@772e2961a17ddc199b25b8b2ec4f4e926c9f9615` (`0.7.1`)  
Tracking issue: #9

This experiment answers one question only:

> Does Reality Gate Lite reproducibly improve first-use clarity or core-action feedback under the same production budget?

It does not add a Runtime phase, a default expert, a memory layer, or a second orchestration path.

## Frozen subject

Use the exact `single-screen-lantern-v1` prompt in
`docs/oneshot-spec-compiler/benchmarks/reality-gate-product-effect.yaml`.
The playable scope is one screen, one interaction loop, success, failure, and
restart. A second level, upgrades, story branches, and external assets are out of
scope.

## Arms

- **A**: unmodified LoopSeed `0.7.1` production and verification.
- **B**: the same Runtime and budget, followed by three observations only:
  First Meaningful Action, Core Action Feedback, and Attention Path.

B may repair defects exposed by those observations. It may not add gameplay or
increase the vertical-slice scope.

## Run discipline

Run three fresh pairs. Use fresh project copies and fresh model context for every
arm. Do not pass discoveries, prompts, screenshots, or criticism from one arm to
another.

Use the fixed order below to reduce order bias:

| Pair | Order |
|---|---|
| P1 | A → B |
| P2 | B → A |
| P3 | A → B |

Both arms must declare the same frozen controls and use the same budget. Compute
the controls fingerprint before running:

```bash
python tools/evaluate_reality_gate_ab.py \
  docs/experiments/v0.8-reality-gate-ab/results.json \
  --print-controls-sha
```

Copy that digest into each arm's `controls_sha256`. This is a declaration receipt,
not proof of hidden token use; wall-clock and cost telemetry must still be recorded
honestly.

## Evidence per arm

Record:

- final candidate commit and artifact SHA-256;
- wall-clock seconds and normalized cost units;
- repair rounds;
- time to first meaningful action and whether it succeeded;
- concrete confusion points;
- concrete feedback and attention-path defects;
- terminal status and whether v0.7.1 integrity validation passed;
- whether scope expanded.

For optional human comparison, blind artifact names before review and record only
`A`, `B`, `TIE`, or `UNAVAILABLE`. Human preference calibrates subjective quality;
it does not replace the predefined metrics.

## Pair validity

Mark a pair invalid and rerun it when seed, start commit, model, surface, budget,
asset access, scope, or acceptance differs between arms. Do not average invalid
pairs into the verdict.

## Decision

```bash
python tools/evaluate_reality_gate_ab.py \
  docs/experiments/v0.8-reality-gate-ab/results.json
```

The evaluator returns:

- `ADMIT`: at least two of three valid pairs improve the same primary dimension,
  without material time/cost regression, scope expansion, or completion regression;
- `REJECT`: the effect is inconsistent, too expensive, scope-dependent, or harms
  completion;
- `STOP_NO_EFFECT`: two consecutive valid pairs show no meaningful effect;
- `INCOMPLETE`: an invalid pair must be rerun;
- `INVALID`: the record is malformed or controls drifted.

Only `ADMIT` authorizes a fresh v0.8 Runtime candidate. Every other result leaves
Reality Gate outside core.
