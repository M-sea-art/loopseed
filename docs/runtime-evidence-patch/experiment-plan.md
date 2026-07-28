# Runtime Evidence Experiment Plan

## Hypothesis

Evidence-governed execution improves autonomous production reliability without requiring more agent layers.

## Comparison

### A - Baseline One-Shot

Natural language goal with standard autonomous execution.

### B - LoopSeed v0.3/v0.4 style

Contract-bound planning, verification, repair loop.

### C - Runtime Evidence Patch

Adds:

- project binding receipt
- executable evidence
- production frontier
- stronger verdict state

## Metrics

Primary:

- false completion rate
- wrong-project execution rate
- human intervention count

Secondary:

- quality uplift
- iteration count
- evidence completeness
- recovery from failed gates

## Stop condition

If v0.5 does not materially improve reliability, do not add further runtime complexity.
