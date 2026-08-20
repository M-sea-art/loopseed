# Optional Whole-Artifact Smoothing Pass

Parallel Gauntlet work can create a peculiar failure mode: many pieces become locally better while the complete artifact becomes slightly less coherent.

Use this pass only when a major wave of independently improved work creates integration debt.

## When to run it

Typical triggers:

- multiple builders changed separate visible or behavioral surfaces;
- individually strong pieces now disagree in style, timing, hierarchy, terminology, interaction, or composition;
- transitions between locally optimized pieces feel rough;
- duplicated or conflicting solutions appeared;
- the whole artifact feels assembled rather than unified.

Do not run a ceremonial smoothing pass after every small repair.

## Smoother contract

Spawn one **fresh** Smoother / Integrator when the environment supports it.

Give it:

- the goal;
- the bar;
- the protected concept commitments, if any;
- the current whole artifact;
- already-passed invariants and do-not-touch regions;
- only the minimum history needed to understand integration constraints.

Its job is to inspect the **complete real artifact** and make it feel like one coherent thing.

It may:

- reconcile visual or stylistic seams;
- repair inconsistent transitions or interaction patterns;
- resolve conflicts between independently changed pieces;
- unify naming, hierarchy, rhythm, spacing, timing, or other cross-part conventions;
- remove accidental duplication introduced by parallel work.

It must not:

- redesign the product wholesale;
- replace the goal or bar;
- erase a protected concept commitment;
- reopen locally frozen wins merely because it prefers another style;
- use `coherence` as an excuse for broad uncontrolled refactoring.

## After smoothing

Treat the smoothing output as a real candidate, not an automatic improvement.

1. Run deterministic regression checks affected by the smoothing changes.
2. Re-observe the whole artifact under the relevant conditions.
3. Re-check protected local wins that the smoothing pass touched.
4. Send materially changed perceptual or behavioral surfaces through the appropriate fresh critic again.
5. Freeze the smoothed version only if it preserves prior wins and improves whole-artifact coherence.

If it damages a frozen local win, repair or roll back.

## Important boundary

The smoothing pass is **optional and secondary**.

The core Gauntlet remains:

```text
split -> build -> judge -> biggest gap -> repair -> repeat
```

Smoothing exists only to counteract the integration seams created when many successful local loops converge on one artifact.
