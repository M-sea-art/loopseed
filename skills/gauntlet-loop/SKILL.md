---
name: gauntlet-loop
description: Apply the Gauntlet Loop method discussed in this skill: establish a real bar, make the actual output observable, separate builder from fresh critic, find the single biggest remaining gap, repair it, compare challenger against incumbent, freeze winners, reject regressions, and repeat only while evidence justifies another round. For inventive work, automatically create and protect a load-bearing concept before convergence.
---

# Gauntlet Loop

This skill is **self-contained**. Apply only the Gauntlet Loop principles defined here. Do not import unrelated project protocols, historical workflows, or remembered architecture from other systems.

Gauntlet Loop is not a framework, engine choice, fixed agent count, or universal production operating system. It is an **evidence-driven quality ratchet**.

Core loop:

```text
GOAL
  ↓
CONCRETE BAR
  ↓
REAL OBSERVATION
  ↓
BUILD / CHALLENGE
  ↓
FRESH CRITIC
  ↓
SINGLE BIGGEST GAP
  ↓
BOUNDED REPAIR
  ↓
BLIND OR DOMAIN-APPROPRIATE COMPARISON
  ↓
FREEZE WINNER / ROLLBACK LOSER
  ↓
REPEAT OR STOP
```

The method exists to prevent an agent from confusing:

```text
I did work
```

with:

```text
The real artifact is actually better.
```

## 1. Route the goal before using the loop

Classify the task so Gauntlet does not become ritual.

### MATCH

The goal is to reproduce, port, imitate, or reach a known target.

- Use that target as the primary bar.
- Skip novelty generation.
- Judge fidelity, behavior, quality, performance, or compatibility against the target.

### INVENT

The value depends on creating something meaningfully unlike existing work.

- Run the one-time **Novelty Gate** before convergence.
- Create and freeze `CONCEPT.md` automatically.
- Use references to judge craft, not to erase originality.

### IMPROVE

A real artifact already exists and should become substantially better.

- Treat the current best as the incumbent.
- Preserve its already-passed behavior and identity.
- Every meaningful change is a challenger that must earn promotion.

### CORRECT

Correctness, compatibility, performance, safety, or specification compliance dominates.

- Tests, measurements, invariants, primary specifications, or formal checks are the bar.
- Blind perceptual A/B is optional and often irrelevant.

### MIXED

The task contains multiple claim types.

Keep the evidence channels separate. Example:

```text
visual quality -> real render + reference comparison
behavior       -> real interaction + state observation
correctness    -> tests + invariants
performance    -> measurements
originality    -> concept invariant + ablation
```

A PASS in one channel never cancels a FAIL in another required channel.

## 2. Choose the smallest useful Gauntlet

Do not spend maximum compute by default.

### MICRO

Use when one bounded defect dominates.

```text
incumbent -> challenger -> fresh critic -> repair or stop
```

### STANDARD

Use for important production work with several judgeable surfaces.

- explicit bar;
- real observation harness;
- separate builder and critic;
- winner freeze;
- regression checks;
- repeated rounds only while useful.

### FULL

Use when the task is high-leverage, perceptually demanding, expensive to get wrong, or explicitly asks for an aggressive Gauntlet.

May include:

- multiple materially different builder routes;
- fresh-context critics;
- randomized and mirrored blind comparison;
- durable evidence packs;
- novelty ablation;
- structural reset after no progress.

Parallelism is optional. Agent count is not the mechanism.

Choose the lowest intensity that can realistically falsify a false completion claim.

## 3. Automatically acquire a real BAR

A bar is not an adjective such as "AAA", "professional", "beautiful", or "high quality".

A valid bar is something an evaluator can actually inspect, run, measure, or test.

Prefer:

1. a user-supplied target or accepted reference;
2. a frozen best version from the same task;
3. real external artifacts with provenance;
4. executable benchmarks, measurements, tests, standards, or specifications;
5. a clearly defined evaluation protocol when no concrete artifact exists.

If no bar is supplied, find or construct the strongest **real** comparison available for the quality claim.

For inventive work:

- prefer references for craft, feel, readability, pacing, polish, interaction, visual cohesion, or performance;
- avoid using a near-clone whose concept would pull the project toward imitation;
- when useful, use several orthogonal references rather than one total reference.

Record provenance for external references in durable runs.

### Bar ratchet

The bar may stay fixed or become harder when stronger evidence is found.

Do not silently lower the bar because the current implementation struggles.

When the agent chooses its own bar, run a separate **Bar Auditor** whose task is to argue that the chosen bar is too soft or too self-serving. Replace it only with an equal or stronger bar.

## 4. Automatically create `CONCEPT.md` for INVENT tasks

When originality is part of the goal, convergence must not begin until the distinct idea is protected.

### Diverge once

Generate a field of meaningfully different candidates. Diversity matters more than a fixed count.

### Novelty Adversary

Reject candidates that are merely:

- `<existing thing> + cosmetic twist`;
- genre defaults with renamed nouns;
- safe feature bundles;
- more complexity without a distinct causal idea.

Prefer candidates whose difference changes what the user **does, perceives, decides, or experiences**.

### Feasibility Critic

Reject concepts whose distinguishing idea cannot plausibly be made observable within the available tools, scope, and budget.

### Ablation Test

For every proposed non-negotiable commitment, ask:

> If this commitment is removed, does the artifact remain essentially the same product?

If yes, it is decoration, not structure.

Reject or replace it before lock.

When affordable, make the ablation concrete through a counterfactual prototype, ruleset, flow, mock, or executable variant. Do not accept a rhetorical claim that "removing it would obviously ruin the project."

### Lock

Write `CONCEPT.md` with:

- one-line product / experience core;
- the causal user loop;
- load-bearing commitments;
- must-not-lose properties.

Then freeze it.

During convergence:

- critics may attack the **execution** of a commitment;
- critics may not call the commitment itself a defect merely because the bar lacks it;
- builders may not soften it merely to make implementation easier.

A locked concept is immutable during ordinary Gauntlet rounds. It may be discarded wholesale only when the real goal changes, decisive external evidence invalidates it, or the owner explicitly kills it.

For long inventive runs, periodically rerun one ablation as a drift alarm. If the artifact now survives without a formerly load-bearing commitment, concept drift outranks ordinary polish.

## 5. Pay the observation tax

A critic must inspect the **real output**, not the builder's description of it.

Use whatever observation method fits the artifact:

- launch and interact;
- render screenshots, video, animation, audio, or 3D views;
- run CLI, API, import/export, build, package, or deployment flows;
- execute tests and benchmarks;
- inspect generated documents, datasets, or reports;
- reproduce a user journey;
- inspect source when the property genuinely requires source evidence.

Do not substitute:

- builder prose for runtime behavior;
- "build passes" for product quality;
- a screenshot for interaction correctness;
- critic opinion for a deterministic test;
- simulated user enthusiasm for real retention or market demand.

If the artifact cannot be observed, create the smallest practical harness before claiming completion.

## 6. Decompose by judgeability

Split the goal into the smallest parts that can be improved and judged independently **without pretending tightly coupled work is independent**.

A good piece has:

- an observable output;
- a clear acceptance surface;
- bounded change scope;
- a clear relationship to the whole artifact.

Ask:

> If this piece fails, can it be repaired without destabilizing the pieces that already passed?

If not, keep the coupled work together.

Fan out only genuinely independent routes. Do not create subagents ceremonially.

## 7. Builder contract

A Builder is responsible for producing a challenger, not approving it.

The Builder should:

1. study the goal, concept invariant if any, bar, incumbent, and current gap;
2. choose a materially useful route;
3. change only what is necessary to test that route;
4. preserve named do-not-touch regions and passed requirements;
5. create the real artifact and evidence needed for evaluation;
6. hand the challenger to an independent critic without self-certifying success.

For FULL runs, multiple builders may take materially different routes. Minor parameter variations do not justify multiple agents.

## 8. Fresh Critic contract

The critic is an independent judge of the artifact, not a collaborator polishing the builder's explanation.

Unless source inspection is required, hide from the critic:

- builder reasoning;
- implementation plan;
- commit messages revealing intended improvements;
- candidate identity;
- previous critic conclusions that could anchor the verdict.

The critic must judge the real output against the declared bar.

When blind comparison is appropriate:

1. anonymize candidates as X / Y or equivalent;
2. use equivalent capture conditions;
3. randomize order;
4. force the critic to choose or rank **before explaining**;
5. state confidence;
6. identify the **single biggest remaining tell / defect**;
7. mirror order in fresh context when position bias could matter;
8. if the mirrored verdict conflicts materially, return `INCONCLUSIVE`.

For deterministic properties, use deterministic evidence instead of forcing an artificial blind test.

A useful critic output is:

```text
VERDICT: PASS | FAIL | X_WINS | Y_WINS | INCONCLUSIVE
CONFIDENCE: low | medium | high
EVIDENCE: <specific observation / state / frame / measurement / failed check>
SINGLE BIGGEST GAP: <one highest-impact remaining problem>
BOUNDED REPAIR: <one repair unit>
DO NOT TOUCH: <already-passed or protected surfaces>
```

See `references/critic-contract.md`.

## 9. The quality ratchet

For each active quality surface:

1. **Freeze the incumbent.** Preserve the current best and its evidence.
2. **Name the weakest meaningful gap.** Prefer the largest user-visible, behaviorally important, correctness-critical, or risk-critical difference.
3. **Build a bounded challenger.** Test one causal improvement route.
4. **Observe the challenger under equivalent conditions.**
5. **Send it to a fresh critic / verifier.**
6. **Compare against the incumbent and bar.**
7. **Demand one primary gap.** Do not turn the round into a giant backlog.
8. **Decide:**
   - challenger clearly wins -> promote and freeze;
   - challenger loses -> rollback;
   - evidence conflicts -> keep incumbent and mark `INCONCLUSIVE`;
   - required deterministic gate fails -> FAIL regardless of aesthetic preference.
9. **Run regression checks** on already-passed surfaces affected by the change.
10. **Repeat only if another round has positive expected value.**

Newer is never automatically better.

## 10. Attack one biggest gap at a time

A critic may see many defects. The next Gauntlet round should normally attack only the highest-impact one.

This preserves causal clarity and reduces regression surface.

"One gap" does not mean "one file". A coherent repair may span many files when one causal defect requires it.

Do not mix unrelated hypotheses into the same quality round.

## 11. Freeze winners and reject regression

A winner must be reproducible enough that later work cannot silently overwrite it.

For durable runs preserve, as practical:

- candidate version or commit;
- evidence artifacts and hashes;
- passed gates;
- protected regions or invariants;
- remaining gap.

If a challenger improves the target gap but breaks something already passed, it is not promoted until the regression is repaired and reverified.

## 12. No-progress means replan

Two consecutive materially similar rounds that fail to improve the same gap trigger root-cause replanning.

Before another build attempt:

1. propose multiple competing explanations for the persistent gap;
2. identify evidence that would distinguish them;
3. choose a materially different route;
4. consider whether the real ceiling is the asset, architecture, model, tool, reference, observation method, or scope.

When local iteration can no longer plausibly reach the bar, use a **STRUCTURAL_RESET** instead of endless cosmetic patching.

A structural reset may replace the implementation route while preserving the goal, concept invariant, and previously proven requirements.

## 13. Stop conditions are part of Gauntlet

Do not equate "the critic can still find flaws" with "the loop must run forever."

For non-trivial runs, use a real budget such as:

- wall-clock time;
- rounds;
- tool calls;
- compute;
- money;
- another explicit resource limit.

Valid outcomes:

- **PASS**: required evidence meets the declared bar.
- **IMPROVED**: materially better, but full bar not proven.
- **INCONCLUSIVE**: evidence cannot support a reliable winner or pass claim.
- **ROLLBACK**: challenger lost; incumbent remains best.
- **STRUCTURAL_RESET**: local iteration is no longer rational.
- **BLOCKED**: an exact external condition prevents useful progress.
- **ABORTED**: owner stops the run.

Budget exhaustion is never PASS.

Stop when:

- the declared bar is met;
- another round has low expected value;
- the budget is reached;
- the route must structurally reset;
- the owner stops the run.

## 14. Product-truth boundary

Gauntlet can strongly support claims such as:

- output more closely matches a real reference;
- a visible or behavioral defect was repaired;
- a real workflow works;
- a quality gap shrank;
- deterministic gates remained green;
- a creative commitment remained load-bearing.

AI-only Gauntlet does not by itself prove:

- users will return tomorrow;
- repeated exposure increases preference;
- a market will pay;
- the target audience finds a game fun;
- a creative artifact will matter culturally.

When these claims matter, label them as requiring external human or market evidence.

## 15. Durable state without bureaucracy

Do not create ceremony for a one-round MICRO Gauntlet.

For multi-round or cross-session work, maintain a lightweight `.gauntlet/` state or equivalent:

```text
.gauntlet/
  RUN.md       # goal, route, intensity, budget, current verdict
  CONCEPT.md   # INVENT only
  BAR.md       # references / tests / metrics / provenance
  RUBRIC.md    # observable properties; may tighten, not silently soften
  PROGRESS.md  # incumbent, current gap, rounds, evidence links
  evidence/    # captures, reports, measurements when useful
```

State exists to preserve causality and evidence, not to create paperwork.

## 16. Minimal autonomous invocation

When the user gives only a goal, the agent should internally resolve:

```text
What kind of task is this: MATCH / INVENT / IMPROVE / CORRECT / MIXED?
What is the strongest concrete bar available?
What observation can falsify a bad result?
Does originality require CONCEPT.md and ablation?
What is the smallest useful Gauntlet intensity?
What is the current incumbent?
What is the single biggest gap?
```

Then execute without making the user manually operate the method unless a real decision, permission boundary, external blocker, or requested review requires human input.

The spirit of the skill is:

> **Let the human state the goal as briefly as possible. Make the agents do the hard work of finding the bar, exposing the real artifact, judging it independently, preserving load-bearing originality, and refusing to call newer work better without evidence.**
