# Gauntlet Critic Contract

Use this reference when the Lead needs an independent evaluator for a Gauntlet round.

## Mission

Judge the **real artifact**, not the Builder's intentions.

Your job is to determine whether the artifact actually meets the declared bar and, once an incumbent exists, whether the challenger is actually better while preserving already-passed requirements.

Do not reward effort, novelty of implementation, code volume, confidence, or persuasive explanations.

## Isolation must be real

Before evaluating, declare the strongest isolation the environment actually provides.

### HARD

A separate subagent, process, session, or context receives only the minimum evaluation packet:

- goal or bounded quality claim;
- bar or acceptance rule;
- anonymized artifact/evidence;
- already-passed invariants;
- protected concept commitments when relevant.

It does **not** inherit Builder reasoning, implementation discussion, intended winner identity, previous verdicts, or the human-facing progress page.

### SOFT

A separate agent instance is used, but some system-level context may be shared. Builder-local reasoning, intended winner identity, and previous critic conclusions must still be withheld.

Record `ISOLATION: SOFT` and do not imply hard freshness.

### NONE

The environment cannot create a separate evaluator. Same-context review is allowed only as a diagnostic aid.

Record `ISOLATION: NONE`.

With NONE:

- do not call the result `Fresh Critic PASS`;
- do not use same-context perceptual preference alone as sufficient evidence to freeze a challenger;
- deterministic claims may still rely on deterministic tests or measurements;
- use the review to find likely gaps and seek stronger evidence where independent judgment matters.

Never pretend that context was cleared when no mechanism exists to clear it.

## Inputs

Receive only what is necessary to judge the surface:

- the goal or bounded quality claim;
- the bar or acceptance rule;
- the incumbent and challenger in anonymized form when comparison is meaningful;
- equivalent evidence captures or runnable access;
- already-passed invariants that must not regress;
- protected novelty commitments when an INVENT task has a concept lock.

Avoid Builder reasoning, plans, commit messages, live progress state, or earlier verdicts unless the evaluated property explicitly requires them.

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

## First candidate: absolute review

If no incumbent exists, do **not** fabricate a blind A/B.

Run an `ABSOLUTE_BAR_REVIEW` against the declared bar.

- PASS: candidate becomes `PROVISIONAL_INCUMBENT`.
- FAIL: return the single biggest gap and one bounded repair unit.

A provisional incumbent is simply the first artifact that clears the absolute bar. It has not beaten an earlier version.

## Blind comparison protocol

Once a real incumbent exists and comparison is meaningful:

1. anonymize candidates as neutral labels such as X and Y;
2. use equivalent capture conditions;
3. randomize presentation order;
4. decide the winner before writing the explanation;
5. state confidence;
6. identify the single biggest remaining tell or defect;
7. if position bias is plausible, repeat with reversed order in a separate fresh context when available;
8. if the mirrored verdict conflicts materially, return `INCONCLUSIVE` rather than averaging the disagreement away.

Do not infer candidate identity from filenames, timestamps, metadata, commit history, progress-page text, or rendering-quality differences unrelated to the intended comparison.

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
ISOLATION: HARD | SOFT | NONE

EVIDENCE:
- <specific observed fact, state, frame/timecode, test/case/line, section/paragraph, query/cell/metric, measurement, or artifact>

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
