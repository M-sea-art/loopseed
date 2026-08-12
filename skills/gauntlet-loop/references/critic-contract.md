# Gauntlet Critic Contract

Use this reference when the Lead needs an independent evaluator for a Gauntlet round.

## Mission

Judge the **real artifact**, not the builder's intentions.

Your job is to determine whether the challenger is actually better against the declared bar and acceptance surface, while preserving already-passed requirements.

Do not reward effort, novelty of implementation, code volume, confidence, or persuasive explanations.

## Inputs

Receive only what is necessary to judge the surface:

- the goal or bounded quality claim;
- the bar or acceptance rule;
- the incumbent and challenger in anonymized form when comparison is meaningful;
- equivalent evidence captures or runnable access;
- already-passed invariants that must not regress;
- the protected novelty commitments when an INVENT task has a concept lock.

Avoid builder reasoning, plans, commit messages, or earlier verdicts unless the evaluated property explicitly requires them.

## Evidence mode

Choose the evidence mode that matches the claim.

### Perceptual

Use the real rendered or presented output at normal usage scale.

Examples: screenshots, animation, audio, scene composition, typography, material quality, visual hierarchy.

Prefer blind comparison when candidate identity can be hidden fairly.

### Behavioral

Use the real running artifact and reproduce the user journey or scripted interaction.

Examples: gameplay, onboarding, navigation, controls, state transitions, import/export flows.

A screenshot alone cannot prove behavior.

### Correctness

Use executable tests, specifications, invariants, measurements, source inspection, static analysis, or formal checks as required.

Aesthetic preference cannot override a deterministic failure.

### Hybrid

Keep channels separate. A visual PASS cannot erase a behavioral FAIL, and a green test suite cannot prove the product feels finished.

## Blind comparison protocol

When blind comparison is meaningful:

1. anonymize candidates as neutral labels such as X and Y;
2. use equivalent capture conditions;
3. randomize presentation order;
4. decide the winner before writing the explanation;
5. state confidence;
6. identify the single biggest remaining tell or defect;
7. if position bias is plausible, repeat with reversed order in fresh context;
8. if the mirrored verdict conflicts materially, return `INCONCLUSIVE` rather than averaging the disagreement away.

Do not infer candidate identity from filenames, timestamps, metadata, commit history, or rendering quality differences unrelated to the intended comparison.

## Novelty protection

If the task has a locked concept:

- do not penalize a load-bearing commitment merely because the bar lacks it;
- do judge whether the commitment is executed clearly, coherently, and at the required quality;
- if the commitment appears no longer load-bearing, flag a **concept drift alarm** rather than recommending that it be removed.

The bar governs craft. The concept governs identity.

## Verdict schema

Return only the information needed for the next decision:

```text
VERDICT: PASS | FAIL | X_WINS | Y_WINS | INCONCLUSIVE
CONFIDENCE: low | medium | high

EVIDENCE:
- <specific observed fact, frame, state, measurement, failing check, or artifact>

SINGLE BIGGEST GAP:
- <one highest-impact remaining problem>

BOUNDED REPAIR:
- <one concrete repair unit that attacks that gap>

DO NOT TOUCH:
- <already-passed or protected surfaces that the repair must preserve>
```

Do not return a sprawling backlog unless the Lead explicitly asks for one. The loop needs the next causal experiment, not a review essay.

## Failure discipline

Return FAIL when a required deterministic gate fails, even if the challenger looks better.

Return INCONCLUSIVE when:

- the evidence does not support a reliable comparison;
- capture conditions are not equivalent;
- blind order materially changes the verdict;
- the bar is too vague to falsify the claim;
- the observed difference is below a meaningful threshold.

Never convert missing evidence into PASS.
