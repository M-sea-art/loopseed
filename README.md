# LoopSeed

**Goal. Bar. Build. Compare. Close the biggest gap. Repeat.**

[简体中文](README.zh-CN.md)

LoopSeed v0.8 is an explicitly invoked, **game-first AI production runtime** built around one simple idea:

> **Gate is the floor. Bar is the ceiling.**

Passing tests, building successfully, or satisfying a stage contract only proves that the work is not broken. It does **not** prove that the result is good enough.

LoopSeed therefore keeps a small Gauntlet-style quality loop at the center of production, while recovery, scheduling, evidence, integrity, and resume logic run underneath as a supporting shell.

```text
GOAL
  ↓
STRONGEST INSPECTABLE BAR
  ↓
agent-owned decomposition
  ↓
BUILD THE REAL THING
  ↓
look · play · run · measure
  ↓
FRESH CRITIC
  ↓
blind / equivalent A-B when useful
  ↓
ONE BIGGEST REMAINING GAP
  ↓
repair · compare again · ratchet the winner
  ↺
```

A v0.8 run cannot write `VERIFIED` from engineering gates alone. It needs current, independent evidence for both:

1. **Hard floors** — the product works and satisfies non-negotiable constraints.
2. **Quality Bar** — the real output reaches or beats the chosen inspectable standard.

---

## Why LoopSeed exists

Modern coding agents can often produce something that runs. The harder problem is preventing them from stopping at the first plausible result.

Common failure modes look like this:

```text
requested: finished game / polished product
      ↓
agent builds: technically valid prototype
      ↓
tests pass
      ↓
agent declares completion
```

LoopSeed changes the objective:

```text
Does it run?                  → hard floor
Does it satisfy the contract? → hard floor
Does the real result hold up against the Bar? → quality decision
```

The runtime is deliberately split into two layers.

### Seed Kernel

The small quality optimizer that should dominate the agent's attention:

```text
Goal → Bar → Build → Inspect → Critic → Biggest gap → Repair → Compare again
```

### Runtime Shell

The machinery that helps the loop survive real projects without taking over the objective:

- recover existing project intent and settled decisions;
- keep Creative Dialogue limited to material ambiguity;
- preserve one product identity and one final integration owner;
- fan out only independently judgeable work;
- refuse idle waiting while safe work remains;
- bind verification to the real Git HEAD and artifact SHA-256;
- require independent, artifact-backed evidence;
- invalidate stale PASS evidence after repairs;
- preserve durable state for resume and recovery;
- fail closed rather than manufacture completion.

The Shell exists to protect the loop. It must not replace the loop.

---

## Quick start

### Small, scoped work

```text
$loopseed <goal>
```

Uses the cheapest useful loop:

```text
Explore → Act → Observe → Verify → Adapt
```

Default topology is one main thread, one writer, and one integration path.

### Full autonomous production

```text
$loopseed one-shotted <natural-language goal>
```

Example:

```text
$loopseed one-shotted Turn the current wuxia cliff-sect prototype into a living,
handcrafted miniature management game. Use the strongest real visual and gameplay
bar you can inspect. Keep the production approach agent-owned. Inspect the running
result, use a fresh critic, attack the single biggest remaining gap each round,
and do not finalize until the hard floors and Bar are independently verified.
```

“One-Shotted” means **one production authorization**, not one model response. Once the intended shot is sufficiently clear, LoopSeed should keep producing, inspecting, repairing, and reverifying without repeatedly asking the user to say “continue.”

You do not need to write a giant specification first. Give LoopSeed the product goal and, when you have one, the strongest real reference or measurable standard that represents success.

---

## The Bar

A Bar must be something an agent can actually inspect or measure.

Good Bars include:

- a reference screenshot compared with a fixed game camera;
- a real product or game flow executed under equivalent conditions;
- a deterministic playtest target;
- a measurable latency, frame-time, quality, or accuracy threshold;
- a blind A/B where a fresh critic prefers the candidate;
- a repeatable task where the candidate must outperform the incumbent.

Weak Bars include:

- “make it premium”;
- “AAA quality” with no inspectable reference;
- “looks good”;
- a source-code claim that never checks the real output.

If the user does not supply a Bar, the Lead should choose the strongest concrete, inspectable standard available instead of inventing a vague adjective.

### Gate vs Bar

A **hard floor** asks whether the product is valid:

- build succeeds;
- complete flow works;
- success, failure, and restart are present;
- performance stays within budget;
- required content exists;
- no P0/P1 defect remains.

A **quality Bar** asks whether the product is actually good enough:

- does the real frame beat the reference in a blind A/B?
- does the interaction feel clearer and more responsive than the incumbent?
- does the finished artifact reach the named production standard?

In v0.8, both are first-class gate roles.

```bash
# Hard floor
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . \
  --id FLOW \
  --title "Complete flow" \
  --criterion "A fresh player can complete, fail, and restart the slice" \
  --owner lead \
  --verifier flow-verifier \
  --machine

# Quality Bar
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . \
  --id BAR \
  --title "Reference comparison" \
  --criterion "In an equivalent blind A/B, the fresh critic prefers the candidate over the locked reference" \
  --owner lead \
  --verifier visual-critic \
  --bar
```

`VERIFIED` requires at least one required hard-floor gate **and** one required quality-bar gate on v0.8.

---

## Real-output criticism

A Critic does not grade the builder's explanation. It inspects the product.

Use the strongest evidence appropriate to the claim:

| Claim | Required observation |
|---|---|
| Visual quality | screenshot / video / running frame |
| Interaction quality | actual playtest / runtime inspection |
| Performance | measurement |
| Build correctness | executed command |
| Product flow | complete real flow |
| Benchmark superiority | direct equivalent comparison |

The Critic should return the **single largest material gap** first. This keeps the repair loop focused and prevents a long review list from becoming a new planning bureaucracy.

When a blind A/B is meaningful, hide builder history and self-justification from the initial critic verdict.

---

## New projects and existing projects

### New project

Start from the goal. Calibrate only when a real product decision remains unresolved.

A game goal may enter `CALIBRATE`, but calibration is not an interview quota. If the idea is already precise enough, synthesize and lock the shot immediately.

### Existing project

LoopSeed first recovers likely planning and decision sources such as:

- `README` / `AGENTS.md`;
- GDDs and product specs;
- roadmaps and milestone docs;
- design / planning / decision records.

Settled decisions are inherited rather than reopened.

Context recovery is independent of Creative Dialogue. Even if you intentionally use `--dialogue off`, discovered project planning still has to be recovered before production proceeds.

If an existing project genuinely has no likely planning source, LoopSeed records a `NONE_FOUND` receipt and continues without manufacturing a human approval gate.

---

## Creative Dialogue

Creative Dialogue is a steering tool, not the engine.

Use it only for choices that can materially change the product result. The model may:

- preserve accepted identity;
- clarify ambiguity;
- correct contradictions;
- amplify the strongest experience;
- complete missing product logic;
- continue previously accepted ideas;
- offer 2–4 meaningfully different options with one recommendation.

Do not ask the user for repository facts, reversible implementation details, or decisions that the project already settled.

After the creative brief is locked, routine production approval returns to the autonomous loop. Weak screenshots, failed tests, or critic failures mean **repair**, not “ask the user whether to continue.”

---

## Controlled Fan-out

Fan-out is an accelerator, not a ceremony.

Good parallel targets:

- isolated asset families;
- read-only research;
- independent tests;
- audio;
- bounded UI surfaces;
- performance profiling.

Keep coupled surfaces under one owner:

- product identity;
- core loop;
- shared runtime state;
- architecture;
- global composition / lighting;
- final integration.

> **Fan out work, not competing interpretations of the product.**

For non-trivial work, `task-graph.json` distinguishes:

- `HARD_DEPENDENCY`;
- `SOFT_ADVICE`;
- `INDEPENDENT`.

The scheduler refuses a wait while safe runnable work remains. Shared write scopes serialize; isolated worktrees may proceed concurrently.

---

## Evidence and integrity

After implementation, LoopSeed freezes a `verification_binding` that ties verification to:

```text
real Git HEAD
+ stable deliverable artifact SHA-256
+ current binding generation
```

Machine gates are executed by the evidence runner. A command written into prose is not evidence.

Observational PASS evidence must point to real project-local artifacts such as screenshots, recordings, or reports, which are hashed when recorded.

If a repair changes the candidate:

1. the old subject is archived;
2. a new binding generation is created;
3. stale PASS claims are reset;
4. the relevant gates are reverified.

This prevents an old screenshot or old test result from certifying a new build.

---

## Production state

```text
CALIBRATE → BIND → PLAN → IMPLEMENT → VERIFY
                                  FAIL ↓    ↓ PASS
                                     REPAIR → VERIFY → FINALIZE
```

Terminal states are strict:

- `VERIFIED` — required hard floors and Bar have current evidence, required work is complete, and no blocking defect remains;
- `BLOCKED` — an exact external condition prevents further safe internal progress and has an exact unblock condition;
- `ABORTED` — the owner explicitly stops the run.

Low quality, failed tests, uncertainty, or an exhausted first approach are not blockers. They trigger repair, rollback, or replanning.

Two consecutive no-progress rounds force root-cause replanning and a materially different route.

---

## Control plane

```text
.loopseed/one-shotted/
├── project-identity.md
├── project-context.json
├── architecture-contract.md
├── goal-contract.json
├── creative-brief.json
├── compiled-shot.md
├── dialogue.jsonl
├── acceptance.json
├── expert-registry.json
├── task-graph.json
├── state.json
├── evidence.jsonl
├── defects.jsonl
└── final-report.json
```

The control plane stores compact decisions and evidence. It is not a chain-of-thought log.

---

## Minimal verification flow

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py init \
  --root . --goal "<goal>"

# Declare at least one hard floor and one Bar before substantial implementation.
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . --id FLOW --title "Flow" --criterion "<observable hard floor>" \
  --owner lead --verifier verifier --machine

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . --id BAR --title "Quality Bar" --criterion "<direct comparison rule>" \
  --owner lead --verifier critic --bar

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition \
  --root . --phase PLAN --next "Plan the smallest route that can win"
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition \
  --root . --phase IMPLEMENT --next "Build the candidate"
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition \
  --root . --phase VERIFY --next "Freeze and verify the real output"

head="$(git rev-parse HEAD)"
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py bind \
  --root . --project "my-project" --candidate "$head" --artifact build/output.zip

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py run-evidence \
  --root . --gate FLOW --actor verifier --command "python tools/verify.py" \
  --project "my-project" --candidate "$head" --artifact build/output.zip

# For an observational Bar, the independent critic records a real hashed artifact.
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py record \
  --root . --gate BAR --result PASS --actor critic \
  --summary "Candidate wins the locked equivalent comparison" \
  --artifact captures/blind-ab-result.png

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py finalize --root .
```

---

## Production modes

- **Focused** — smallest coherent result, minimum useful topology.
- **Studio** — presentation-ready game or product slice with the relevant quality disciplines.
- **Moonshot** — raises the experiential ceiling while keeping an explicit scope guard.

A higher mode does not authorize more ceremony. It authorizes more quality ambition where the Bar justifies it.

---

## Cost discipline

LoopSeed follows a simple escalation rule:

```text
one thread is enough      → do not fan out
one real comparison works → do not build an evaluation bureaucracy
one critic is enough      → do not create a review committee
machine evidence works    → do not replace it with prose
```

Two governance rules remain non-negotiable:

> **No new mechanism without demonstrated product effect.**

> **Every new control must replace more uncertainty than complexity it introduces.**

---

## Validate locally

```bash
python -m json.tool .codex-plugin/plugin.json >/dev/null
find skills/loopseed/schemas skills/loopseed/templates -name '*.json' -print0 \
  | xargs -0 -n1 python -m json.tool >/dev/null
python tools/verify_usage_guide_version.py
python -m compileall -q hooks skills/loopseed/scripts tests tools
python -m unittest discover -s tests -v
```

## More detail

- [Production usage guide — 中文](docs/usage-guide.zh-CN.md)
- [One-Shotted mode](skills/loopseed/references/one-shotted-mode.md)
- [Autonomy after lock](skills/loopseed/references/autonomy-after-lock.md)
- [State contracts](skills/loopseed/references/state-contract.md)
- [Runtime ladder](skills/loopseed/references/runtime-ladder.md)
- [Acknowledgements](ACKNOWLEDGEMENTS.md)

## License

MIT. See [LICENSE](LICENSE).
