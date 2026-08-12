# Adaptive Gauntlet Routing

This reference helps a Lead decide **whether and how** to apply Gauntlet Loop without turning every task into an expensive multi-agent production ritual.

## Decision 1: what kind of value is being optimized?

### MATCH

Signals:

- "make this match..."
- "recreate / port / reproduce / clone the behavior"
- "bring our version up to this reference"

Default route:

```text
explicit target -> observation harness -> incumbent/challenger loop
```

Do not run novelty divergence.

### INVENT

Signals:

- the user wants an original product, game, experience, concept, visual language, interaction, or mechanism;
- a derivative answer would fail even if technically polished;
- identity and novelty are part of the value proposition.

Default route:

```text
one-time novelty gate -> concept lock -> orthogonal craft bar -> convergence loop
```

### IMPROVE

Signals:

- a current artifact exists;
- the user says improve, polish, refine, optimize, make production-ready, make it feel finished;
- scope identity should remain stable.

Default route:

```text
freeze current best -> find biggest gap -> bounded challenger -> independent comparison
```

### CORRECT

Signals:

- correctness, reliability, safety, compatibility, regression risk, performance, build integrity, or standards compliance dominates;
- the result can be falsified by tests or measurements.

Default route:

```text
spec/invariants/tests -> focused repair -> fresh verification -> regression
```

Use A/B only if it adds information.

### MIXED

Signals:

- the task combines product quality with correctness;
- a game must both feel good and run correctly;
- a UI must look polished and remain accessible;
- a 3D asset must look good and import correctly;
- a report must be insightful and numerically correct.

Default route:

```text
separate evidence channels -> one integrated verdict that fails closed on required channels
```

## Decision 2: is Gauntlet worth the cost?

Ask:

1. Can bad quality survive ordinary implementation checks?
2. Is there a concrete bar, test, measurement, or observation protocol?
3. Will the artifact be reused, shipped, judged, or relied on enough that extra evaluation has value?
4. Is there a meaningful incumbent/challenger comparison to make?
5. Can another round plausibly change the outcome?

If most answers are no, do not run a full Gauntlet.

## Decision 3: choose intensity

### MICRO

Choose when:

- one defect dominates;
- the artifact is small;
- turnaround matters more than exhaustive proof;
- a single fresh review is enough to catch self-approval.

Typical topology:

```text
Lead/Builder -> one real observation -> fresh Critic -> repair or stop
```

### STANDARD

Choose when:

- several quality surfaces matter;
- the artifact will ship or be reviewed;
- regression risk exists;
- the current best needs to be protected across rounds.

Typical topology:

```text
Lead
  -> bounded Builder
  -> real evidence
  -> independent Critic
  -> winner freeze / rollback
  -> regression
```

### FULL

Choose when:

- quality is difficult to reach through a single path;
- perceptual judgment matters strongly;
- the task is high leverage or expensive to redo later;
- materially different implementation routes are available;
- the user explicitly requests aggressive iteration.

Possible topology:

```text
Lead
  -> Builder route A
  -> Builder route B
  -> optional Scout / domain expert
  -> Evidence packager
  -> fresh blind Critic
  -> mirrored Critic when useful
  -> winner freeze / rollback / structural reset
```

Do not create parallel agents for coupled work merely to imitate this diagram.

## Domain examples

### Game development

Evidence channels may include:

- player input and first-minute understanding;
- complete start -> play -> success/failure -> restart loop;
- screenshots and short gameplay recordings;
- animation, camera, audio, hit feedback, pacing;
- FPS, frame time, load time, build/package/relaunch;
- real target-player playtests for claims about fun or retention.

### 3D assets

Evidence channels may include:

- turntable or fixed-view renders;
- silhouette and material comparisons;
- topology/mesh checks;
- scale, orientation, skeleton, animation, UV, naming;
- actual import into the target engine and runtime inspection.

### UI / web / app

Evidence channels may include:

- equivalent viewport screenshots;
- interactive user flows;
- accessibility checks;
- responsive breakpoints;
- performance measurements;
- reference products for hierarchy and polish.

### Backend / library / SDK

Evidence channels may include:

- contract tests;
- compatibility suites;
- property tests;
- benchmarks;
- primary-source API or standards requirements;
- source review for architecture or security claims.

Blind perceptual A/B is usually secondary here.

### Writing / reports

Evidence channels may include:

- user-supplied style or publication references;
- factual/source verification;
- structure and audience requirements;
- blind comparison for clarity or voice when useful;
- deterministic checks for data, citations, or required sections.

### Research / analysis

Evidence channels may include:

- primary-source support;
- reproducible calculations;
- competing hypotheses;
- falsification tests;
- independent re-analysis;
- explicit uncertainty and evidence limits.

## Automatic downshift rules

Downshift FULL -> STANDARD or STANDARD -> MICRO when:

- builder routes are not truly independent;
- evidence capture dominates implementation cost;
- the bar is already clearly met;
- the same verifier can deterministically prove the claim;
- the remaining issue is a tiny bounded repair;
- the user prioritizes speed over marginal quality.

## Automatic escalation rules

Escalate MICRO -> STANDARD or STANDARD -> FULL when:

- the same visible gap survives a repair;
- the builder and verifier disagree about reality;
- a high-cost regression appears;
- the current bar is much stronger than the incumbent;
- independent routes could expose a local optimum;
- the user explicitly wants maximum quality and the budget permits it.

## Honest exit

The Lead should always be able to say:

```text
The artifact improved, but the bar is not yet proven.
```

That sentence is a successful Gauntlet outcome when the evidence demands it.
