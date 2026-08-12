# Gauntlet Loop Principles and Limits

This note explains the reasoning behind the skill so an agent can adapt the method instead of mechanically imitating a prompt.

## 1. Gauntlet is a judge-and-repair strategy, not a complete production OS

The method is strongest after there is something real to inspect.

It complements systems that handle:

- goal calibration;
- project binding;
- scheduling;
- dependency management;
- permissions;
- delivery and release state.

Its special strength is refusing the false inference:

```text
we implemented it
therefore
it is good enough
```

## 2. Engineering PASS is necessary but not sufficient for product PASS

A build can compile, tests can pass, exports can succeed, and the user-visible result can still be obviously unfinished, confusing, static, generic, or broken in a path the tests did not exercise.

Therefore keep separate gates for:

- engineering integrity;
- real behavior;
- perceptual/product quality;
- external user preference when required.

One gate does not inherit the authority of another.

## 3. The evaluator must touch reality

The core anti-self-deception move is not "use another model." It is:

> make the evaluator inspect the real output through the strongest available observation channel.

A fresh critic that only reads the builder's explanation is still trapped inside the builder's story.

The observation tax can be a browser harness, engine run, replay, test suite, benchmark, render sheet, packaged build, import test, API probe, or another domain-appropriate instrument.

## 4. Freshness reduces anchoring, not epistemic limits

Fresh context is useful because it reduces contamination from:

- the builder's intent;
- sunk-cost sympathy;
- previous rationalizations;
- expected winner identity.

But freshness does not magically make a weak evaluator strong.

Use deterministic evidence for deterministic claims, domain experts for domain-specific claims, and real users for human preference claims.

## 5. Blind comparison is a tool, not a religion

Blind A/B is powerful when:

- the outputs can be presented under equivalent conditions;
- the claim is comparative;
- identity leakage can be controlled;
- the evaluator can meaningfully perceive the difference.

It is weak or irrelevant when:

- correctness is best proven by tests;
- security requires source and threat analysis;
- candidate conditions cannot be normalized;
- the task has no meaningful reference comparison.

When used, blind comparison should force a decision before the explanation so the evaluator cannot hide inside vague review prose.

## 6. Improvement means challenger beats incumbent

Newer is not better.

Every substantial repair is an experiment:

```text
incumbent + evidence
        vs
challenger + equivalent evidence
```

If the challenger loses, roll it back.

If the evidence conflicts, keep the incumbent and say INCONCLUSIVE.

This is the quality ratchet.

## 7. One biggest gap preserves causal clarity

A critic can usually name dozens of defects. Repairing many at once makes it difficult to know what produced improvement and creates unnecessary regression surface.

Prefer:

- the largest user-visible gap;
- the most severe behavioral defect;
- the highest-risk correctness failure;
- the bottleneck whose removal unlocks the next quality level.

Then repair one bounded unit and re-observe.

This is not a ban on coherent multi-file changes. It is a ban on mixing unrelated hypotheses into one quality round.

## 8. No-progress is information

If two materially similar repair rounds do not improve the same gap, the correct response is not "try harder in the same way."

Treat the failure as evidence about the causal model.

Possible ceilings include:

- wrong root cause;
- wrong decomposition;
- asset ceiling;
- model capability ceiling;
- tool limitation;
- architecture limitation;
- reference mismatch;
- observation error;
- scope contradiction.

Replan or structurally reset.

## 9. Parallelism is conditional

Gauntlet is often associated with builder/critic fan-out, but agent count is not the mechanism.

Parallelism helps when:

- routes are materially different;
- write ownership is isolated;
- outputs can be judged independently;
- selection value exceeds coordination cost.

Parallelism hurts when:

- the artifact's identity is tightly coupled;
- multiple agents fight over shared state;
- integration cost hides the quality signal;
- every route is a minor variant of the same idea.

A single strong builder plus a fresh critic can be a valid Gauntlet.

## 10. Creative work needs a second axis besides resemblance

Pure reference convergence can erase originality. A strange or novel choice may look like a "tell" simply because the reference does not contain it.

For tasks whose value depends on invention, separate two questions:

```text
Is the execution good enough?     -> bar / critic / tests
Is the distinct idea still real?  -> novelty invariant / ablation
```

The critic may demand better execution of the idea, but may not erase the idea for the sake of resemblance.

## 11. Ablation turns novelty from rhetoric into structure

A distinctive commitment is load-bearing only if removing it changes the product materially.

Ablation asks:

```text
What remains if we remove this supposed core idea?
```

If the answer is "basically the same product," the novelty is decorative.

This check is especially useful before freezing an inventive concept and later as a drift alarm.

## 12. The bar is a ceiling and a hazard

A weak bar caps quality.

A near-clone bar can also distort identity.

Therefore:

- acquire real references rather than imagined adjectives;
- choose references for the specific craft being judged;
- use multiple orthogonal references when no single artifact is appropriate;
- keep provenance;
- never silently soften the bar during a difficult run.

## 13. Cost is part of quality strategy

A loop that improves quality by consuming unbounded time or model calls is not automatically efficient.

Track a real budget when the run is non-trivial.

Useful signals include:

- rounds per accepted improvement;
- reverted or discarded work;
- evidence-generation cost;
- builder/critic calls;
- wall-clock time;
- tool or compute spend;
- remaining gap at stop.

The right question is not "did Gauntlet use more resources?" but:

> did the additional evaluation reduce high-cost wrong-direction work or meaningfully raise the final bar enough to justify itself?

## 14. AI-only product truth has a hard boundary

An AI critic can detect defects, compare artifacts, run flows, and expose self-deception.

It cannot independently establish real-world desire.

For claims such as retention, repeated enjoyment, willingness to pay, cultural resonance, or target-audience delight, preserve a separate external truth gate.

Do not turn simulated users into fabricated market evidence.

## 15. The shortest useful mental model

```text
BAR tells us what good looks like.
OBSERVATION tells us what we actually made.
CRITIC tells us the largest remaining difference.
REPAIR tests one causal response.
RATCHET keeps only proven wins.
NOVELTY INVARIANT prevents creative convergence from sanding off the point.
STOP RULE prevents quality ambition from becoming infinite ritual.
```

That is the method. Everything else is implementation detail.
