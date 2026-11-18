# Quality methods

For an open vision, use a method when it answers a real question about the work. The following requirements apply when the owner selects One-Shotted delivery.

## Seed Kernel

The Seed Kernel owns product-quality convergence. Keep it cognitively small.

```text
GOAL
  ↓
INSPECTABLE BAR
  ↓
agent-owned decomposition
  ↓
bounded builder
  ↓
REAL OUTPUT
  ↓
fresh independent critic
  ↓
blind A/B when meaningful
  ↓
SINGLE BIGGEST GAP
  ↓
bounded repair
  ↓
freeze winner / rollback loser
  ↺
```

### Kernel rules

1. Prefer a concrete, inspectable bar over adjectives.
2. The Lead chooses the decomposition. Do not ceremonially fan out.
3. Judge the real artifact or running product, not builder prose.
4. Builder and critic are different roles. The builder cannot approve its own gate.
5. Blind the comparison when candidate identity can bias the verdict.
6. Ask for one biggest material gap, not a giant review backlog.
7. Attack that gap with one coherent repair hypothesis.
8. Promote only a challenger that wins without breaking already-passed surfaces.
9. Two materially similar no-progress rounds force root-cause replanning and a materially different route.
10. Do not silently soften the bar because the run is difficult.
11. Do not let reference convergence erase the user's load-bearing original idea. The bar governs craft; the concept governs identity.
12. Budget exhaustion, missing evidence, or an inconclusive comparison is never PASS.
13. **Judge games in motion when motion matters.** A still-image win cannot prove animation, camera motion, battle readability, interaction, timing, feedback, or game-feel superiority.
14. **Critics inspect first-hand.** When the environment permits, the fresh critic launches, plays, operates, or views the real candidate and captures its own screenshots/clips/measurements. It must not inherit the builder's interpretation as its primary evidence.
15. **Judge generated assets in product context.** An isolated sprite, render, model, animation, or effect may pass asset sanity checks, but it cannot receive final in-product quality PASS until judged inside the real scene, camera, lighting, scale, UI, animation, and runtime conditions that materially affect it.
16. **Re-globalize after Fan-out.** After each major parallel improvement wave, run one fresh whole-product critic across the integrated result before opening the next wave. Its job is to find the single largest cross-surface inconsistency created or exposed by local improvements.
17. **Synthesize a Bar when reality has no close complement.** If no meaningful real-world Bar exists, generate or otherwise construct the strongest inspectable representation of the intended result, freeze it as a `Synthetic Bar`, and compare against it. A synthetic visual Bar can define visual intent; it cannot substitute for behavioral, interaction, or performance evidence.

### Choosing the bar

Use the strongest bar the agent can actually inspect.

Prefer, in order:

1. **Real Bar** - a real product, reference state, incumbent, benchmark, or measurable target that corresponds to the claim.
2. **Synthetic Bar** - a generated or deliberately constructed target representation when the intended product has no meaningful real-world complement.
3. **Hybrid Bar** - separate real and synthetic channels when different quality surfaces require different references.

Examples:

- visual game/UI: real reference screenshots at equivalent viewport and state;
- motion/game feel: reference clips or runtime sequences under equivalent camera/input conditions;
- gameplay: scripted run plus a reference flow, incumbent build, or measurable first-minute target;
- original visual concept with no close real complement: generated target frames frozen before implementation and compared against equivalent runtime captures;
- 3D asset: reference render plus engine import, integrated scene, animation, scale, and runtime checks;
- software: executable spec, benchmark, compatibility suite, or known-good incumbent;
- writing/report: supplied publication/style reference plus factual/structural requirements.

When no single reference is appropriate, use a hybrid bar with separate evidence channels. A green correctness channel cannot erase a perceptual FAIL, and a beautiful screenshot cannot erase a broken behavioral path.

Do not allow a Synthetic Bar to become a moving target. Freeze the selected reference set before judging the corresponding candidate generation. If the product concept legitimately changes under user authority, explicitly regenerate/rebind the Bar rather than silently moving it.

## Critic contract

A critic receives only what is necessary to judge the declared surface:

- the goal or bounded claim;
- the frozen real/synthetic/hybrid Bar;
- anonymized incumbent/challenger when comparison is meaningful;
- equivalent captures or runnable access;
- protected invariants and already-passed surfaces.

Hide builder reasoning, confidence, commit chronology, and candidate identity until the initial verdict.

For games and interactive products, the preferred critic path is first-hand:

```text
launch / play / operate real candidate
  ↓
capture critic-owned screenshots + clips + measurements
  ↓
place against equivalent Bar evidence
  ↓
blind or mirrored comparison when meaningful
  ↓
name one biggest gap
```

If the critic cannot access the runtime, it must disclose that limitation. It may judge only the surfaces directly supported by the available evidence and must not PASS motion, interaction, or game-feel claims from still images alone.

Preferred verdict form:

```text
VERDICT: PASS | FAIL | X_WINS | Y_WINS | INCONCLUSIVE
CONFIDENCE: low | medium | high

EVIDENCE:
- <specific first-hand observed fact / frame / clip / state / measurement>

SINGLE BIGGEST GAP:
- <one highest-impact remaining problem>

BOUNDED REPAIR:
- <one coherent repair unit>

DO NOT TOUCH:
- <already-passed or identity-critical surfaces>
```

If mirrored blind judgments materially disagree, return `INCONCLUSIVE`; do not average disagreement into fake precision.

## Ratchet

Newer is not automatically better.

For every meaningful challenger:

- challenger wins -> promote and freeze;
- challenger loses -> roll back;
- deterministic hard gate fails -> FAIL regardless of aesthetics;
- evidence is insufficient or ordering changes verdict -> INCONCLUSIVE;
- two similar failed repair rounds -> root-cause replan / structural reset.

Preserve, as practical:

- candidate commit/version;
- evidence artifacts and hashes;
- passed gates;
- protected invariants;
- remaining biggest gap.

## Evidence rules

- Running without errors is not visual acceptance.
- Source files are not completion evidence.
- Visual claims require visual inspection.
- Motion claims require motion evidence when motion materially affects quality.
- A still-image win cannot prove animation, camera motion, interaction, timing, battle readability, or game-feel superiority.
- Interaction claims require runtime/playtest inspection.
- Performance claims require measurement.
- Generated assets must be judged in the integrated product context before final in-product quality PASS when scene/camera/lighting/scale/UI/animation materially affect them.
- An isolated render may prove asset sanity; it cannot by itself prove integrated product quality.
- A command string is not evidence unless `run-evidence` executed it against the bound clean candidate.
- Observational PASS evidence must name at least one real project-local artifact whose SHA-256 remains stable.
- A fresh critic should capture its own evidence when capability permits instead of relying only on builder-selected evidence.
- A worker cannot approve its own gate.
- Missing evidence never becomes PASS.
