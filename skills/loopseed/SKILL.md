---
name: loopseed
description: Run a Gauntlet-first, evidence-governed production loop from an explicit `$loopseed` goal. Use `$loopseed one-shotted` when one authorization should launch autonomous planning, implementation, real-output criticism, repair, and fail-closed finalization.
---

# LoopSeed v0.8 - Gauntlet Kernel

Use only after an explicit `$loopseed` invocation. Never infer activation from similar wording or an old state file.

LoopSeed is a game-first AI production engine with a small quality kernel inside a durable runtime shell.

## The invariant

```text
Goal tells us what to make.
Bar tells us what good looks like.
Observation tells us what we actually made.
Fresh Critic tells us the single biggest remaining difference.
Repair tests one causal response.
Ratchet keeps proven wins.
Runtime Shell prevents forgetting, drift, fake evidence, and unsafe concurrency.
```

**Gate is the floor. Bar is the ceiling.**

A build, test suite, artifact contract, or stage gate may prove that the candidate is valid enough to judge. It does not by itself prove that the product is good enough.

For v0.8 One-Shotted runs, `VERIFIED` requires both:

1. at least one required `hard` gate is PASS; and
2. at least one required `bar` gate is PASS.

If the hard gates pass but the real output still loses to the declared quality bar, the run is not VERIFIED. Continue, replan, roll back, hit an honest budget stop, or let the owner stop the run.

## Operating modes

- **Standard:** `$loopseed <goal>` - smallest useful Explore -> Act -> Observe -> Critique -> Adapt loop.
- **One-Shotted:** `$loopseed one-shotted <goal>` - one production authorization launches a durable run.

One-Shotted means one production authorization, not one model response.

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

### Choosing the bar

Use the strongest bar the agent can actually inspect.

Examples:

- visual game/UI: real reference screenshots at equivalent viewport and state;
- gameplay: scripted run plus a reference flow, incumbent build, or measurable first-minute target;
- 3D asset: reference render plus engine import/runtime checks;
- software: executable spec, benchmark, compatibility suite, or known-good incumbent;
- writing/report: supplied publication/style reference plus factual/structural requirements.

When no single reference is appropriate, use a hybrid bar with separate evidence channels. A green correctness channel cannot erase a perceptual FAIL, and a beautiful screenshot cannot erase a broken behavioral path.

## Runtime Shell

The Runtime Shell exists to support the kernel, not compete with it for attention.

It provides:

- project-context recovery;
- Project Binding and Artifact Contract;
- task ownership and safe fan-out;
- no-idle scheduling;
- evidence ledgers and SHA-256 artifact binding;
- independent gate verification;
- defect tracking and repair routing;
- durable resume state;
- fail-closed terminal receipts.

Treat this machinery as background infrastructure. Do not make the user manage it unless an external authorization is genuinely required.

## Shared authority

Bind one root goal and acceptance to this order:

1. the user's explicit current instruction and accepted decisions;
2. the locked creative brief, when one was actually needed;
3. named project plans, milestones, product specifications, and reference files;
4. repository instructions such as `AGENTS.md`;
5. tests and the running product as evidence.

Existing implementation is evidence, not authority when it conflicts with intended product identity.

## Start path: minimal language, maximum leverage

### New or already-clear project

Do not open a creative interview just because the domain is a game.

Prefer:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py init \
  --root . \
  --goal "<goal>" \
  --dialogue off
```

Then declare the smallest hard floors and one explicit quality bar:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . \
  --id BUILD \
  --title "Runnable build" \
  --criterion "The target build/package launches and the required flow completes" \
  --owner lead \
  --verifier verifier \
  --machine

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . \
  --id BAR \
  --title "Inspectable product bar" \
  --criterion "In equivalent evidence, the candidate meets or beats <named reference / incumbent / metric> while preserving the locked concept" \
  --owner lead \
  --verifier fresh-critic \
  --bar
```

Do not invent extra gates simply to make the protocol look thorough.

### Existing project

Recover settled intent before changing product direction.

Inspect likely planning sources such as `README`, `AGENTS.md`, `docs/`, design/planning/product/spec directories, roadmaps, GDDs, briefs, milestones, and decision records.

Recover at least:

- sources inspected and their authority role;
- inherited decisions that must continue;
- genuinely open material decisions;
- unresolved conflicts or stale planning;
- a compact current-project synthesis.

Never ask the user for facts already present in authoritative project material. Never downgrade an existing plan merely because a simpler implementation is easier.

### When creative dialogue is justified

Use `--dialogue on` only when an unresolved product decision can materially change the result and cannot be recovered from the user instruction or project authority.

During `CALIBRATE`:

- preserve settled identity;
- clarify only material ambiguity;
- correct contradictions with the tradeoff stated;
- amplify the strongest differentiator;
- offer 2-4 meaningfully different options when a real choice remains;
- recommend one;
- stop asking once the shot is precise enough.

Do not ask low-level reversible implementation questions. Do not reopen settled planning. Do not continue interviewing merely because dialogue rounds remain.

## Production modes

- **Focused** - smallest coherent result quickly; no idea expansion.
- **Studio** - default game-production target; coherent presentation-ready vertical slice with game feel, art direction, playtest, asset, and performance evidence.
- **Moonshot** - deliberately raise the experiential ceiling with bounded fan-out. State both ambition expansion and scope guard.

Moonshot means raise the experience, not multiply features without limit.

## One-Shotted production

After goal/brief authority and gates are bound:

1. freeze Project Binding, Artifact Contract, and target stage;
2. ensure at least one required hard-floor gate and one required bar gate exist;
3. assign implementation owner and a different verifier;
4. choose the smallest complete route that can plausibly beat the bar;
5. record non-trivial work in `task-graph.json`;
6. classify relations as `HARD_DEPENDENCY`, `SOFT_ADVICE`, or `INDEPENDENT`;
7. dispatch every safe runnable node before waiting;
8. keep coupled identity, core loop, architecture, composition, and final integration under one owner;
9. merge into one candidate and observe the real output;
10. compare candidate against the bar and incumbent under equivalent conditions;
11. let the fresh critic return one biggest gap;
12. repair, reobserve, and recompare;
13. bind the clean real Git HEAD and stable deliverable for verification;
14. run machine gates with `run-evidence` and observational gates with hashed artifacts;
15. finalize only when all required hard gates and required bar gates PASS with current bound evidence.

## Critic contract

A critic receives only what is necessary to judge the declared surface:

- the goal or bounded claim;
- the bar;
- anonymized incumbent/challenger when comparison is meaningful;
- equivalent captures or runnable access;
- protected invariants and already-passed surfaces.

Hide builder reasoning, confidence, commit chronology, and candidate identity until the initial verdict.

Preferred verdict form:

```text
VERDICT: PASS | FAIL | X_WINS | Y_WINS | INCONCLUSIVE
CONFIDENCE: low | medium | high

EVIDENCE:
- <specific observed fact / frame / state / measurement>

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

## No-idle scheduling

The Lead retains scheduling responsibility after delegation.

- `HARD_DEPENDENCY` blocks only its direct consumer.
- `SOFT_ADVICE` never blocks execution.
- `INDEPENDENT` permits concurrent progress when write ownership is safe.
- A shared write scope has one writer.
- Separate worktrees or isolation boundaries may run overlapping scopes concurrently.
- Waiting is legal only when no safe runnable node remains and named work is already running.
- If a task becomes runnable while a wait is declared, validation fails with `NO_IDLE_WHILE_RUNNABLE`.

Fan out work, not product identity.

## Evidence rules

- Running without errors is not visual acceptance.
- Source files are not completion evidence.
- Visual claims require visual inspection.
- Interaction claims require runtime/playtest inspection.
- Performance claims require measurement.
- A command string is not evidence unless `run-evidence` executed it against the bound clean candidate.
- Observational PASS evidence must name at least one real project-local artifact whose SHA-256 remains stable.
- A worker cannot approve its own gate.
- Missing evidence never becomes PASS.

## Autonomy after lock

After the goal/brief is aligned, do not return to the user for ordinary production approval.

Do not ask the user to approve screenshots, architecture, reversible implementation choices, asset selection, critic findings, repair direction, test results, or whether to continue.

Human re-entry is exceptional and reserved for an exact condition outside the run's authority or capability, such as credentials/2FA, payment or purchase, legal/account authorization, irreversible external publication, or an explicit owner checkpoint.

Weak quality is a repair signal, not a blocker.

## State machine

```text
CALIBRATE? -> BIND -> PLAN -> IMPLEMENT -> VERIFY
                                  FAIL ↓      ↓ PASS hard + bar
                                     REPAIR -> VERIFY -> FINALIZE
```

`CALIBRATE` is optional. The kernel does not require dialogue when Goal + Bar are already clear.

## Terminal discipline

- `VERIFIED` - all required tasks settle, all required hard-floor gates PASS, at least one required bar gate exists and every required bar gate PASSes with current bound evidence, no P0/P1 defect remains, and the terminal receipt cross-validates.
- `BLOCKED` - an exact irreplaceable external condition prevents further safe progress and states the exact unblock condition.
- `ABORTED` - the owner explicitly stops the run.

Failure, low quality, a losing challenger, uncertainty, or an exhausted first route are not blockers. They trigger repair, rollback, replanning, or an honest non-PASS stop.

## Reporting

At the end report only:

- terminal verdict;
- direct evidence and final report path;
- changed scope;
- quality-bar result;
- remaining non-blocking risk;
- exact unblock condition when blocked.

An ordinary LoopSeed invocation does not authorize changing LoopSeed itself.
