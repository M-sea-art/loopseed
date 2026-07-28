# Project Binding Receipt

**Experiment arm:** `C0 PROTOCOL_ONLY`

- Canonical project: LoopSeed v0.5 Runtime Evidence Patch experiment
- Repository: `/workspace/scratch/5c121f59219d/loopseed-v05-experiment`
- Branch: `experiment/evidence-governed-runtime-v0.5`
- Commit baseline: `d50e92fdaed5f7cb6a0ccb3054a341cf823a19e8`
- Target artifact: `docs/runtime-evidence-patch/runs/2026-07-28-t1/arm-c0/artifact`
- Stage: isolated C0 builder run
- Runtime protocol: frozen LoopSeed v0.3.0 One-Shotted control plane with the fixed v0.5 Evidence-Governed overlay
- Product: runnable single-screen browser-game vertical slice, 《雨夜客栈：守灯人》

## Protected invariants

1. The builder writes only inside the target artifact directory.
2. The product must run without external assets, dependencies, network access, or public deployment.
3. The product has exactly three nights; each night requires one consequential traveler choice.
4. Lamp units visibly decrease after every choice.
5. Night three ends in a choice-dependent ending.
6. Runtime evidence is limited to three screenshots.
7. Execution, evidence, quality, and terminal states remain separate.
8. This arm is protocol-only evidence and does **not** claim that an executable LoopSeed v0.5 Runtime has been validated.
