---
name: gauntlet-loop
description: Apply a self-contained Gauntlet Loop quality ratchet: run inside a real agentic harness, resolve a concrete inspectable bar, expose the real artifact, separate builders from fresh critics, attack the single biggest remaining gap, compare challenger against incumbent, freeze proven wins, roll back regressions, smooth whole-artifact coherence when parallel work drifts, and repeat without an arbitrary round cap while evidence justifies another round. Supports a Matt-style minimal launcher, hard/soft critic isolation, first-candidate absolute review, live progress reporting, and originality protection for inventive work.
---

# Gauntlet Loop

This skill is **self-contained**. Apply only the Gauntlet Loop principles defined here. Do not import unrelated project protocols, historical workflows, or remembered architecture from other systems.

Gauntlet Loop is not a framework, engine choice, fixed agent count, or universal production operating system. It is an **evidence-driven quality ratchet**.

Its purpose is simple:

> **Make errors progressively harder to disguise as completion.**

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

The human should be able to state the goal briefly. The agents do the hard work of finding the bar, exposing reality, judging independently, and refusing to call newer work better without evidence.

## 0. Agentic Harness Gate

A real Gauntlet Loop requires an execution environment that can **touch the artifact**.

Prefer an agentic harness such as Claude Code, Codex, or another environment that can, as relevant:

- open and modify files;
- run code, tests, builds, benchmarks, or scripts;
- launch and interact with the product;
- render or inspect screenshots, video, audio, pages, documents, or other outputs;
- use tools needed to observe the result;
- create separate subagents or contexts for independent critics when available.

A normal chat that cannot inspect or change the real artifact may still:

- design a Gauntlet;
- choose or critique a bar;
- generate the short launcher prompt;
- review evidence supplied by the user.

But it must **not pretend it executed a full Gauntlet Loop** when it could not touch the artifact or instantiate the required evaluation conditions.

The method depends on an evaluator inspecting reality, not a model imagining what the result probably looks like.

## 1. Minimal invocation first

Gauntlet should feel lightweight to invoke even when the underlying method is rigorous.

A sufficient user request is:

```text
Run a Gauntlet Loop for: <goal>
References: <optional references>
```

Or simply:

```text
/gauntlet <goal>
```

When the user gives only a goal, the Lead must internally resolve:

```text
What is the strongest concrete bar available?
What can the evaluator actually inspect, run, compare, or measure?
What is the current incumbent, if any?
Does originality need protection before convergence?
What is the smallest useful decomposition?
Which pieces are actually independent enough to fan out?
What is the cheapest evidence that can falsify a false completion claim?
```

Do not make the user manually operate the protocol unless a real product decision, permission boundary, external blocker, or explicitly requested review requires human input.

### Minimal prompt compiler

When the user asks for a prompt for Claude Code, Codex, or another agent, compile the goal and bar into a short launcher rather than dumping this whole skill into the prompt.

The launcher should preserve this shape:

```text
I want you to achieve: <GOAL>

Quality bar: <BAR>. Compare the real output directly against it.

Choose the approach yourself. Break the goal into the smallest pieces that can be improved and judged independently. For each important independent piece, use a builder and a separate fresh-context critic when the environment supports it. Each critic must inspect the real output, compare it with the bar, identify the single biggest remaining gap, and send that gap back for another round. Use blind A/B comparison when it is genuinely meaningful. Keep only proven wins, roll back regressions, and keep looping without an arbitrary round cap until the output meets or beats the bar, further improvements become too small to matter, the available compute budget is exhausted, a structural reset is required, or I stop the run.

Maintain a simple live progress page for me that shows the artifact evolving over time, but never expose that page or builder reasoning to blind critics. After major parallel waves, use an optional fresh whole-artifact smoothing pass when the pieces need coherence. Use subagents and ultracode when the environment provides them and they add value.
```

Keep the compiled launcher short. The **prompt is the ignition key; this skill is the engine**.

See `references/minimal-invocation.md`.

## 2. Route the goal before looping

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

Keep evidence channels separate:

```text
visual quality -> real render + reference comparison
behavior       -> real interaction + state observation
correctness    -> tests + invariants
performance    -> measurements
originality    -> concept invariant + ablation
```

A PASS in one channel never cancels a FAIL in another required channel.

## 3. Choose the smallest useful Gauntlet

Do not spend maximum compute by default.

### MICRO

Use when one bounded defect dominates.

```text
incumbent -> challenger -> real observation -> fresh critic -> repair or stop
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
- whole-artifact smoothing after major waves;
- structural reset after no progress.

Parallelism is optional. Agent count is not the mechanism.

Choose the lowest intensity that can realistically falsify a false completion claim.

## 4. Automatically acquire a real BAR

A bar is not an adjective such as `AAA`, `professional`, `beautiful`, or `high quality`.

A valid bar is something an evaluator can actually inspect, run, compare, or measure.

Prefer:

1. a user-supplied target or accepted reference;
2. a frozen best version from the same task;
3. real external artifacts with provenance;
4. executable benchmarks, measurements, tests, standards, or specifications;
5. a clearly defined evaluation protocol when no concrete artifact exists.

If no bar is supplied, find or construct the strongest **real** comparison available for the quality claim. The chosen bar should play the same functional role that a real side-by-side reference plays in a visual imitation task: it gives the critic something outside the builder's story to judge against.

For inventive work:

- prefer references for craft, feel, readability, pacing, polish, interaction, visual cohesion, or performance;
- avoid using a near-clone whose concept would pull the project toward imitation;
- when useful, use several orthogonal references rather than one total reference.

Record provenance for external references in durable runs.

### Aspirational bar doctrine

A strong bar does **not** need to be realistically reachable in the current run.

A deliberately difficult real-world reference can still provide direction and prevent the agent from stopping at `pretty good for AI`.

Therefore:

- the run may legitimately stop while still below the bar;
- the final verdict may be `IMPROVED` rather than `PASS`;
- the owner may stop when satisfied;
- improvements may stop when gains become too small to matter or compute is no longer worth spending;
- the bar must never be silently weakened to manufacture a win.

### Bar ratchet

The bar may stay fixed or become harder when stronger evidence is found.

Do not silently lower the bar because the current implementation struggles.

When the agent chooses its own bar and the choice is material, use a separate **Bar Auditor** to challenge whether the bar is too soft, uninspectable, or self-serving. Replace it only with an equal or stronger bar.

## 5. Protect originality for INVENT tasks

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

If yes, it is decoration, not structure. Reject or replace it before lock.

When affordable, make the ablation concrete through a counterfactual prototype, ruleset, flow, mock, or executable variant.

### Lock

Write `CONCEPT.md` with:

- one-line product or experience core;
- the causal user loop;
- load-bearing commitments;
- must-not-lose properties.

Then freeze it.

During convergence:

- critics may attack the **execution** of a commitment;
- critics may not call the commitment itself a defect merely because the bar lacks it;
- builders may not soften it merely to make implementation easier.

A locked concept is immutable during ordinary Gauntlet rounds. It may be discarded wholesale only when the real goal changes, decisive external evidence invalidates it, or the owner explicitly kills it.

For long inventive runs, periodically rerun one ablation as a drift alarm.

## 6. Pay the observation tax

A critic must inspect the **real output**, not the builder's description of it.

Use a domain-neutral evidence interface:

```text
ARTIFACT               -> the thing actually being judged
OBSERVATION CONDITIONS -> viewport, environment, dataset, inputs, run configuration, audience condition, etc.
EVIDENCE CHANNEL       -> render, interaction, test, benchmark, source inspection, document review, measurement, etc.
EVIDENCE LOCATOR       -> frame/timecode, state, test/case/line, section/paragraph, query/cell/metric, artifact path, etc.
DETERMINISTIC CHECKS   -> claims that can be mechanically falsified
PERCEPTUAL/BEHAVIORAL CHECKS -> claims that require inspection or use
```

Choose the observation method required by the artifact:

- launch and interact;
- render screenshots, video, animation, audio, or 3D views;
- run CLI, API, import/export, build, package, or deployment flows;
- execute tests and benchmarks;
- inspect generated documents, datasets, or reports;
- reproduce a user journey;
- inspect source when the property genuinely requires source evidence.

Do not substitute:

- builder prose for runtime behavior;
- `build passes` for product quality;
- a screenshot for interaction correctness;
- critic opinion for a deterministic test;
- simulated user enthusiasm for real retention or market demand.

If the artifact cannot be observed, create the smallest practical harness before claiming completion.

## 7. Decompose by judgeability

Split the goal into the smallest parts that can be improved and judged independently **without pretending tightly coupled work is independent**.

A good piece has:

- an observable output;
- a clear acceptance surface;
- bounded change scope;
- a clear relationship to the whole artifact.

Ask:

> If this piece fails, can it be repaired without destabilizing the pieces that already passed?

If not, keep the coupled work together.

The Lead decides which pieces should be separated, which should stay together, and which can run in parallel. Do not predefine the workstreams merely because a generic template lists them.

Fan out only genuinely independent routes. Do not create subagents ceremonially.

### Subagents and ultracode

When the execution environment exposes subagents, use them where independent work and fresh criticism benefit from isolation. When it exposes an `ultracode` mode or equivalent high-capability coding mode, use it when the task justifies the extra capability and the user requested it.

Do not invent nonexistent tools, and do not treat agent count or ultracode as the mechanism of quality. The mechanism remains **real evidence + independent criticism + a winner-preserving ratchet**.

## 8. Builder contract

A Builder is responsible for producing a challenger, not approving it.

The Builder should:

1. study the goal, concept invariant if any, bar, incumbent, and current gap;
2. choose a materially useful route;
3. change only what is necessary to test that route;
4. preserve named do-not-touch regions and passed requirements;
5. create the real artifact and evidence needed for evaluation;
6. hand the challenger to an independent critic without self-certifying success.

For FULL runs, multiple builders may take materially different routes. Minor parameter variations do not justify multiple agents.

## 9. Critic instantiation and isolation

A `Fresh Critic` is not merely the same agent changing roles. The Lead must first discover what isolation the environment can actually provide.

### `HARD`

Use a genuinely separate subagent, process, session, or context that receives only the minimum evaluation packet:

```text
GOAL or bounded quality claim
BAR / RUBRIC
anonymized artifact or evidence
already-passed invariants
protected concept commitments, when relevant
```

It must not inherit Builder reasoning, implementation discussion, intended winner identity, or previous critic verdicts.

`HARD` is the preferred mode for perceptual or comparative promotion decisions.

### `SOFT`

Use a separate agent instance when some system-level context may be shared but Builder-local reasoning and candidate identity can still be withheld.

Record:

```text
isolation: SOFT
```

A SOFT verdict may promote a candidate when evidence is strong and the relevant leakage controls are satisfied, but the report must not claim stronger isolation than actually existed.

### `NONE`

If the environment cannot instantiate a genuinely separate evaluator, same-context re-evaluation is permitted only as a diagnostic aid.

Record:

```text
isolation: NONE
```

With `NONE`:

- do not call the result `Fresh Critic PASS`;
- do not treat a same-context perceptual preference as sufficient evidence for L3-style promotion;
- use deterministic evidence for deterministic claims;
- use the same-context critic to locate likely gaps, then seek stronger evidence if the decision materially depends on independent judgment.

Never pretend to have cleared context when the environment provides no such capability.

See `references/critic-contract.md`.

## 10. Fresh Critic contract

The critic is an independent judge of the artifact, not a collaborator polishing the builder's explanation.

Unless source inspection is required, hide from the critic:

- builder reasoning;
- implementation plan;
- commit messages revealing intended improvements;
- candidate identity;
- previous critic conclusions that could anchor the verdict;
- the human-facing live progress page.

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
ISOLATION: HARD | SOFT | NONE
EVIDENCE: <specific observation / state / frame / measurement / failed check>
SINGLE BIGGEST GAP: <one highest-impact remaining problem>
BOUNDED REPAIR: <one repair unit>
DO NOT TOUCH: <already-passed or protected surfaces>
```

## 11. First candidate: no fake A/B

A Gauntlet may start with no incumbent. Do not fabricate a baseline merely to satisfy an A/B shape.

If `incumbent == NONE`:

```text
candidate
  ↓
ABSOLUTE_BAR_REVIEW
  ↓
PASS -> candidate becomes PROVISIONAL_INCUMBENT
FAIL -> repair the SINGLE_BIGGEST_GAP and review again
```

A provisional incumbent is simply the first real artifact that clears the minimum absolute bar. It is not evidence that the process has beaten an earlier version.

Once a real incumbent exists, challenger rounds may use comparative blind A/B where meaningful.

## 12. The quality ratchet

For each active quality surface:

1. **Freeze the incumbent.** Preserve the current best and its evidence.
2. **Name the weakest meaningful gap.** Prefer the largest user-visible, behaviorally important, correctness-critical, or risk-critical difference.
3. **Build a bounded challenger.** Test one causal improvement route.
4. **Observe the challenger under equivalent conditions.**
5. **Send it to the strongest available fresh critic or verifier.**
6. **Compare against the incumbent and bar.**
7. **Demand one primary gap.** Do not turn the round into a giant backlog.
8. **Decide:**
   - challenger clearly wins -> promote and freeze;
   - challenger loses -> rollback;
   - evidence conflicts -> keep incumbent and mark `INCONCLUSIVE`;
   - required deterministic gate fails -> FAIL regardless of aesthetic preference.
9. **Run regression checks** on already-passed surfaces affected by the change.
10. **Repeat without an arbitrary fixed round count** while another round has positive expected value.

Newer is never automatically better.

## 13. Attack one biggest gap at a time

A critic may see many defects. The next Gauntlet round should normally attack only the highest-impact one.

This preserves causal clarity and reduces regression surface.

`One gap` does not mean `one file`. A coherent repair may span many files when one causal defect requires it.

Do not mix unrelated hypotheses into the same quality round.

## 14. Freeze winners and reject regression

A winner must be reproducible enough that later work cannot silently overwrite it.

For durable runs preserve, as practical:

- candidate version or commit;
- evidence artifacts and hashes;
- passed gates;
- protected regions or invariants;
- remaining gap.

If a challenger improves the target gap but breaks something already passed, it is not promoted until the regression is repaired and reverified.

## 15. No-progress means replan

Two consecutive materially similar rounds that fail to improve the same gap trigger root-cause replanning.

Before another build attempt:

1. propose multiple competing explanations for the persistent gap;
2. identify evidence that would distinguish them;
3. choose a materially different route;
4. consider whether the real ceiling is the asset, architecture, model, tool, reference, observation method, or scope.

When local iteration can no longer plausibly reach the bar, use a **STRUCTURAL_RESET** instead of endless cosmetic patching.

A structural reset may replace the implementation route while preserving the goal, concept invariant, and previously proven requirements.

## 16. Optional whole-artifact smoothing pass

When many builders improve separate pieces, local wins can accumulate into a globally inconsistent artifact.

At the end of a **major parallel wave**, the Lead may spawn one fresh **Smoother / Integrator** to inspect the complete real artifact before the next wave.

Its job is narrow:

- inspect the whole artifact, not isolated pieces;
- detect seams, conflicts, duplicated decisions, style drift, transition problems, or integration inconsistencies;
- make the parts feel like one coherent thing;
- preserve already-proven local wins and protected concept commitments;
- avoid redesigning the product or reopening every local decision.

The smoothing pass is **optional**, not the core loop. Use it when parallel local optimization creates integration debt.

After smoothing:

- rerun deterministic regression checks affected by the changes;
- re-observe the whole artifact;
- send materially changed quality surfaces through the appropriate critic again.

See `references/smoothing-pass.md`.

## 17. Live progress page

For non-trivial or multi-round runs, maintain a simple human-facing progress surface so the owner can watch the work evolve **without interrupting the agents**.

It should show useful operational state and, where appropriate, real evolving media:

```text
Goal
Chosen bar
Current incumbent
Current quality surface
Current single biggest gap
Round history
Freeze / rollback / inconclusive events
Evidence links
Screenshots / video clips / drafts / test results / rendered outputs / other useful previews
Current status
```

The Lead may implement this as a simple live HTML page, `workbench.md`, or the simplest environment-appropriate continuously updated artifact. Do not prescribe a web framework merely to satisfy this requirement.

### Anti-leak rule

The progress page is for the **human and Lead only**.

Do not provide it to blind critics. Do not let candidate labels, intended fixes, previous verdicts, or round history leak from the progress page into a fresh critic packet.

The progress page is a control surface, never completion evidence by itself.

See `references/live-progress.md`.

## 18. Stop conditions are part of Gauntlet

Do not equate `the critic can still find flaws` with `the loop must run forever`.

Do **not** prescribe a fixed number of rounds in advance. A sufficiently ambitious bar may remain above the artifact throughout the run.

For non-trivial runs, track a real budget such as:

- wall-clock time;
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

`Keep looping until our output wins or I stop` should be interpreted with this discipline:

```text
WIN / PASS
or owner says it is ready
or improvements become too small to matter
or compute is no longer worth spending
or ROLLBACK
or INCONCLUSIVE
or STRUCTURAL_RESET
or external BLOCKED
or owner stops
```

Budget exhaustion is never PASS. Never weaken the bar merely to manufacture a win.

## 19. Product-truth boundary

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

## 20. Durable state without bureaucracy

Do not create ceremony for a one-round MICRO Gauntlet.

For multi-round or cross-session work, maintain a lightweight `.gauntlet/` state or equivalent:

```text
.gauntlet/
  RUN.md          # goal, route, intensity, budget, current verdict
  CONCEPT.md      # INVENT only
  BAR.md          # references / tests / metrics / provenance
  RUBRIC.md       # observable properties; may tighten, not silently soften
  PROGRESS.md     # incumbent, current gap, rounds, evidence links
  progress-page/  # optional human-facing live progress surface
  evidence/       # captures, reports, measurements when useful
```

State exists to preserve causality and evidence, not to create paperwork.

## 21. Final report

At the end, state only what the evidence supports:

- final outcome;
- bar used and whether it was met;
- strongest isolation level actually achieved;
- incumbent / final winner;
- significant rollback or inconclusive events;
- whether a smoothing pass was used and what whole-artifact issue it addressed;
- remaining biggest gap, if any;
- evidence locations;
- external product-truth claims that remain unproven.

A successful Gauntlet run proves only what this run and its evidence establish. It does not prove that Gauntlet is universally superior to other workflows.

## Short mental model

```text
AGENTIC HARNESS lets the method touch reality.
BAR tells us what great looks like.
OBSERVATION tells us what we actually made.
BUILDER produces a challenger.
FRESH CRITIC exposes the largest remaining difference.
REPAIR tests one causal response.
RATCHET keeps only proven wins.
SMOOTHING reconnects locally optimized pieces when parallel work creates seams.
NOVELTY INVARIANT prevents convergence from sanding off the point.
PROGRESS PAGE lets the human watch without contaminating the critic.
STOP RULE prevents ambition from becoming infinite ritual.
```
