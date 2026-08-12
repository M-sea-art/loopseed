---
name: gauntlet-loop
description: Apply an adaptive, evidence-grounded quality ratchet when a task benefits from repeated build-observe-critic-repair cycles. Use for creative production, visual or UX polish, games, prototypes, code quality, behavior, research artifacts, or existing work that must be pushed against a concrete bar. Automatically choose a perceptual, behavioral, correctness, or hybrid Gauntlet; protect load-bearing originality when invention matters; skip or downshift the loop when the evaluation cost would exceed its expected value.
---

# Gauntlet Loop

Gauntlet Loop is a **quality strategy**, not a fixed architecture, game framework, or mandatory multi-agent ritual.

Its purpose is simple:

```text
make the real output observable
        ↓
compare it against a concrete bar
        ↓
find the single highest-impact remaining gap
        ↓
repair only that gap
        ↓
challenge the incumbent with fresh evidence
        ↓
freeze the winner, reject regressions, repeat only when useful
```

The loop exists to make it hard for an agent to confuse **work performed** with **quality achieved**.

Use this skill either when explicitly requested or when the current task clearly needs a quality ratchet. Do not activate it merely because subagents are available.

## 1. Route before looping

First classify the task. The classification determines what Gauntlet means.

### MATCH

The user wants to reproduce, match, port, imitate, or reach a known target.

- The target itself is the primary bar.
- Skip creative divergence.
- Judge resemblance, behavior, fidelity, performance, or compatibility against the target.

### INVENT

The task's value depends materially on being unlike existing work.

- Run the one-time **Novelty Gate** before convergence.
- Protect the resulting concept as an invariant.
- Use bars for craft and execution quality, not for copying the concept.

### IMPROVE

A real artifact already exists and the goal is to make it substantially better.

- The current best artifact is the incumbent.
- Preserve the user-owned identity and already-passed behavior.
- Every change is a challenger that must beat the incumbent on the named gap without regression.

### CORRECT

The dominant question is correctness, safety, compatibility, performance, or specification compliance.

- Executable tests, invariants, measurements, formal checks, or primary-source requirements are the bar.
- Blind A/B may be irrelevant.
- A fresh verifier may inspect source when source inspection is necessary to prove the property.

### MIXED

Most serious product work is mixed.

Use separate evidence channels for separate claims. For example:

```text
visual quality   -> real render + reference comparison
interaction      -> scripted use + state observation
correctness      -> tests + invariants
performance      -> benchmark measurements
originality      -> novelty invariant + ablation
product preference -> real users, not an AI-only claim
```

Never let one green channel overwrite a failure in another.

## 2. Choose the smallest useful intensity

Gauntlet should be **adaptive**, not ceremonial.

### MICRO

Use when the task is bounded, cheap, or one repair is likely enough.

- one incumbent;
- one challenger;
- one fresh critic/verifier;
- one concrete gap;
- one repair round unless evidence justifies another.

### STANDARD

Use for important production work with multiple independently judgeable quality surfaces.

- explicit bar and rubric;
- real observation harness;
- independent builder and critic roles;
- incumbent/challenger ratchet;
- regression checks;
- bounded repeated rounds.

### FULL

Use when the artifact is high-leverage, expensive to get wrong, perceptually demanding, or the user explicitly asks for an aggressive Gauntlet.

- multiple materially different builder routes only where independence is real;
- fresh-context critics;
- randomized or mirrored blind comparisons when appropriate;
- durable evidence packs;
- novelty ablation for inventive work;
- structured no-progress and structural-reset logic.

Choose the lowest intensity that can falsify a false completion claim.

## 3. Acquire a real bar

A bar is not an adjective. It is something the evaluator can inspect, execute, measure, or test.

Prefer, in order:

1. a user-supplied target or accepted reference;
2. a previously frozen best version from the same project;
3. real external artifacts with provenance;
4. executable benchmarks, tests, standards, measurements, or specifications;
5. a clearly declared evaluation protocol when no artifact comparison exists.

Do not invent evidence and then grade against the invention.

For inventive work, use references **orthogonally**:

- reference craft, readability, pacing, material quality, interaction clarity, performance, or production finish;
- do not select a near-clone whose concept would pull the project toward imitation.

The bar may rise when stronger evidence is found. Do not silently lower it to make the run pass.

Record provenance for external references when the run is durable.

## 4. Make the real output observable

The critic must be able to inspect the thing that the user will actually receive or experience.

Choose the observation method required by the task:

- launch and interact with a game or app;
- render and inspect images, video, animation, audio, or 3D assets;
- execute CLI flows, APIs, builds, imports, exports, or packaging;
- run tests and benchmarks;
- inspect generated reports, documents, or datasets;
- reproduce a user journey;
- inspect source only when the evaluated property genuinely lives in source.

Do not substitute:

- builder prose for runtime behavior;
- a passing build for product quality;
- a screenshot for interaction correctness;
- a critic's impression for a deterministic test;
- an AI playtester for real retention or market demand.

If the output cannot be observed, create the smallest practical harness before claiming quality.

## 5. The one-time Novelty Gate for INVENT tasks

Run this only when originality is part of the task's value. Do not run it on straightforward replication, migration, repair, or compliance work.

### Diverge once

Generate a field of meaningfully different concepts. Scale the number of candidates to the budget; diversity matters more than a fixed count.

### Novelty adversary

Reject concepts that are merely:

- an existing thing with a cosmetic twist;
- safe feature bundles;
- genre defaults with renamed nouns;
- complexity without a distinct causal idea.

Prefer concepts whose differentiator changes what the user **does, perceives, decides, or experiences**.

### Feasibility critic

Reject concepts whose distinguishing idea cannot plausibly be made observable within the authorized scope, tools, and budget.

### Ablation

For each proposed non-negotiable commitment, test the counterfactual:

> If this commitment is removed, does the artifact remain essentially the same product?

If yes, the commitment is decoration, not structure. Reject or replace it before lock.

The ablation must be grounded in a concrete counterfactual design, prototype, ruleset, flow, or executable variant when affordable. Do not accept a purely rhetorical claim that "removing it would obviously ruin the project."

### Lock the concept

Freeze a concise concept containing:

- the one-line product or experience core;
- the user-facing causal loop;
- the load-bearing commitments;
- explicit must-not-lose properties.

During convergence:

- a critic may attack the **execution** of a commitment;
- a critic may not call the commitment itself a defect merely because the bar does not contain it;
- a builder may not soften it to make implementation easier.

A locked concept is **immutable, not immortal**. It may be killed wholesale by explicit user instruction, decisive external product-validation failure, or a hard contradiction with the real goal. It may not be gradually diluted by builders or critics.

For long inventive runs, periodically rerun one ablation as a drift alarm. If the artifact now survives without a formerly load-bearing commitment, creative drift outranks ordinary polish work.

## 6. Decompose by judgeability, not by org chart

Split the goal into the smallest pieces that can be improved and judged independently **without lying about coupling**.

Good units have:

- an observable output;
- a named acceptance surface;
- a bounded write scope;
- a clear relationship to the whole artifact.

Do not fan out tightly coupled identity, architecture, composition, shared state, or final integration merely to increase agent count.

Parallelize only when different routes can proceed independently and the expected value exceeds coordination cost.

A useful question is:

> If this piece fails, can I repair it without destabilizing the pieces that already passed?

If not, the decomposition is probably wrong or the work must stay under one owner.

## 7. Run the quality ratchet

For each active quality surface:

1. **Freeze the incumbent.** Preserve the current best and its evidence.
2. **Name the weakest meaningful gap.** Prefer the largest user-visible, behaviorally important, correctness-critical, or risk-critical gap.
3. **Build a bounded challenger.** Change only what is needed to test a materially better route.
4. **Observe the real challenger.** Reproduce the same evidence conditions used for the incumbent.
5. **Use a fresh critic/verifier.** Keep it independent from the builder's reasoning and self-justification.
6. **Compare.** Use blind A/B or mirrored order when that creates a meaningful falsifiable comparison; otherwise use the strongest domain-appropriate test.
7. **Demand one primary gap.** The critic names the single highest-impact remaining defect or tell.
8. **Decide.**
   - challenger clearly wins -> freeze it as the new incumbent;
   - challenger loses -> roll back;
   - evidence conflicts -> keep the incumbent and mark INCONCLUSIVE;
   - deterministic gate fails -> FAIL regardless of aesthetic preference.
9. **Regress.** Recheck already-passed surfaces that the change could affect.
10. **Repeat only if another round has positive expected value.**

Do not distribute the repair budget evenly across many mediocre surfaces. Attack the weakest high-impact surface first.

## 8. Fresh critic contract

A critic is not a collaborator polishing the builder's explanation. It is an independent judge of the artifact.

Unless the task requires source review, hide from the critic:

- builder reasoning;
- implementation plan;
- commit messages that reveal the intended winner;
- candidate identity labels;
- previous critic conclusions that would anchor the new verdict.

When blind comparison is appropriate:

- randomize candidate identity;
- use equivalent capture conditions;
- require the critic to choose or rank before explaining;
- mirror the order when position bias could matter;
- treat disagreement as evidence, not noise to average away.

A good verdict contains:

```text
winner / PASS / FAIL / INCONCLUSIVE
confidence
specific evidence
single biggest remaining gap
one bounded repair unit
do-not-touch regions
```

See `references/critic-contract.md` for the full evaluator contract.

## 9. Preserve winners and reject regression

The ratchet only works if success cannot be silently overwritten.

For durable runs, preserve enough information to reproduce the best state:

- candidate version or commit;
- evidence artifacts and hashes when practical;
- passed gates;
- protected regions or invariants;
- remaining gap.

A new candidate is not "progress" merely because it is newer.

If it improves the target gap but breaks a previously passed requirement, it is not a winner until the regression is repaired and reverified.

## 10. No-progress and structural reset

Do not grind the same local patch forever.

Two consecutive rounds that fail to materially change the same gap trigger **root-cause replanning**.

Before another build attempt:

1. propose multiple competing explanations for why the gap persists;
2. identify evidence that would distinguish them;
3. choose a materially different route;
4. consider whether the true ceiling is an asset, architecture, model, tool, reference, or scope boundary.

When the current route cannot plausibly reach the bar, use a **STRUCTURAL_RESET** rather than cosmetic iteration.

A reset may replace the implementation route while preserving the goal, concept invariant, and already-proven requirements.

## 11. Stopping is part of the method

Before or during a durable run, choose a budget appropriate to the task: wall-clock time, tool calls, compute, money, review rounds, or another real constraint.

Valid outcomes:

- **PASS**: the required evidence meets the bar.
- **IMPROVED**: the artifact is materially better, but the full bar is not proven.
- **INCONCLUSIVE**: the evidence cannot support a winner or pass claim.
- **ROLLBACK**: the challenger lost and the incumbent remains best.
- **STRUCTURAL_RESET**: local iteration is no longer rational.
- **BLOCKED**: an exact external condition prevents further useful progress.
- **ABORTED**: the owner stops the run.

Budget exhaustion is not PASS.

Do not loop forever merely because a critic can always find another flaw. Stop when the declared bar is met, the expected value of another round is too low, the budget is reached, or the route must be reset.

## 12. Product-truth boundary

Gauntlet can provide strong evidence that:

- an output more closely matches a reference;
- a defect was repaired;
- a workflow works;
- a visual or behavioral gap shrank;
- engineering integrity was preserved;
- an inventive commitment remained load-bearing.

AI-only Gauntlet does **not** by itself prove:

- users will return tomorrow;
- people prefer the product after repeated exposure;
- a market will pay;
- a game is fun for its target audience;
- a creative work will be culturally important.

When those claims matter, hand off to real user or market evidence and label the current result honestly.

## 13. Durable run state

Do not create ceremony for a one-round MICRO Gauntlet.

For multi-round or cross-session work, maintain a lightweight `.gauntlet/` directory or equivalent project-local state:

```text
.gauntlet/
  RUN.md          # goal, route, intensity, budget, current verdict
  CONCEPT.md      # only for inventive work that requires a lock
  BAR.md          # references, tests, metrics, provenance
  RUBRIC.md       # observable properties; may tighten, not silently soften
  PROGRESS.md     # incumbent, current gap, rounds, evidence links
  evidence/       # captures, reports, measurements when useful
```

Keep it small. The state exists to preserve causality and evidence, not to create paperwork.

## 14. Interaction with LoopSeed

Gauntlet Loop and LoopSeed are complementary.

Use LoopSeed for:

- goal calibration;
- creative brief and product binding;
- production planning and scheduling;
- task ownership;
- engineering evidence and finalization.

Use Gauntlet Loop when a quality surface needs a stricter incumbent/challenger ratchet:

```text
LoopSeed chooses and binds what must be built
        ↓
production creates a real candidate
        ↓
Gauntlet challenges quality with independent evidence
        ↓
LoopSeed preserves integration, task state, and engineering integrity
```

Do not make every LoopSeed task enter FULL Gauntlet. Route it only to the surfaces where another quality round has real expected value.

## 15. Minimal invocation pattern

When the user gives only a goal, the Lead should internally resolve:

```text
What kind of task is this: MATCH / INVENT / IMPROVE / CORRECT / MIXED?
What evidence channel can actually falsify a bad result?
What is the strongest concrete bar available?
Does originality need a one-time novelty lock?
What is the smallest useful Gauntlet intensity?
What is the current incumbent?
What is the single biggest gap?
```

Then execute. Do not burden the user with the machinery unless a real product decision, permission boundary, external blocker, or requested report requires it.

The spirit of the skill is:

> **Let the human state the goal as briefly as possible. Make the agents do the hard work of finding the right bar, exposing the real artifact, judging it independently, and refusing to call newer work better without evidence.**
