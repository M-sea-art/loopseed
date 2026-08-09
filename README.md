# LoopSeed

**Aim through dialogue. Ignite with One-Shot. Accelerate with Fan-out. Let evidence decide.**

[简体中文](README.zh-CN.md)

LoopSeed is an explicitly invoked, **game-first AI production engine**. It helps a player or creator turn an unfinished game idea into a precise, ambitious production brief through creative dialogue, then launches one uninterrupted, evidence-governed production run.

It can also handle general software and product work through a lighter domain adapter.

```text
player seed
    ↓
creative co-director dialogue
preserve · correct · amplify · complete · continue · offer options
    ↓
user-authorized creative brief
    ↓
One-Shot production
    ↓
controlled Fan-out
    ↓
integration · playtest · visual review · performance gates
    ↓
VERIFIED / BLOCKED / FAIL evidence
```

LoopSeed is deliberately both **ambitious and strict**:

- the creative phase may enlarge the strongest experience;
- production may fan out aggressively when work is truly independent;
- the final verdict may never exceed the evidence.

## Two execution modes

### Standard LoopSeed

```text
$loopseed <goal>
```

Uses the cheapest sufficient loop:

```text
Explore → Act → Observe → Verify → Adapt
```

It defaults to one thread, one writer, and one integration path.

### One-Shotted production

```text
$loopseed one-shotted <natural-language goal>
```

“One-Shotted” means **one production authorization**, not necessarily one user message and not one model response.

For game ideas, LoopSeed normally enters a creative dialogue first. Once the user-authorized brief is locked, it plans, implements, delegates independent work, integrates, tests, captures evidence, repairs defects, and finalizes without repeatedly asking the user to say “continue.”

## Game-first creative dialogue

The user can start with a seed rather than a completed design document.

During dialogue, the model acts as a co-director that may:

- preserve the original game identity;
- explain and correct contradictions;
- amplify the strongest player experience;
- complete missing product logic;
- continue ideas already accepted by the user;
- offer two to four meaningful choices with one recommendation and clear consequences.

Each round must move a material decision. It must not repeat answered questions, ask for repository facts, push reversible implementation details back to the user, or silently replace the requested game with an easier artifact.

The default cap is five model question rounds, but it is a ceiling, not a target. Clear ideas lock sooner.

## Production modes

### Focused

Complete the smallest coherent result quickly. Do not expand the product idea.

### Studio

The default game route. Build a coherent, presentation-ready vertical slice with game identity, Art Bible, game feel, assets, complete play flow, visual evidence, and performance gates.

### Moonshot

Deliberately amplify the strongest experience and use aggressive but bounded Fan-out. Moonshot requires both an ambition expansion and a scope guard.

Moonshot deepens the experience; it does not authorize uncontrolled feature growth or inflated completion claims.

## Initialize

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py init \
  --root . \
  --goal "Build a living wuxia sect-management vertical slice"
```

Optional controls:

```text
--domain auto|game|general
--production-mode auto|focused|studio|moonshot
--dialogue auto|on|off
--max-dialogue-rounds 1..8
```

Defaults:

- detected game goals enter `CALIBRATE`;
- general goals enter `BIND` on the focused route;
- explicit Moonshot or dialogue flags can override the automatic route.

## Record a dialogue choice

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py dialogue-turn \
  --root . \
  --actor model \
  --kind question \
  --summary "Choose how the first slice proves that the sect is alive" \
  --effect preserve \
  --effect amplify \
  --advance core_loop \
  --advance hero_moment \
  --option "A|Three-day crisis|A complete bounded management loop" \
  --option "B|Cinematic scene|More spectacle but weaker gameplay proof" \
  --option "C|Large sandbox|More breadth but lower completion confidence" \
  --recommended A
```

Record the user's natural-language answer, compile the accepted decisions into a creative brief, then lock it:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py lock-brief \
  --root . \
  --file creative-brief.json
```

The lock writes `creative-brief.json` and `compiled-shot.md`, then moves the run from `CALIBRATE` to `BIND`. Production gates cannot be declared before this user-authorized lock.

## Game production contract

A locked game brief defines the relevant subset of:

- player promise and role;
- core loop and world response;
- unique hook;
- Art Bible and game feel;
- hero moment and vertical-slice boundary;
- asset strategy and placeholder replacement;
- complete playthrough, success, failure, and restart;
- fixed screenshots and isolated subject review;
- FPS, frame time, draw calls, triangles, memory, load time, build, package, and relaunch;
- forbidden substitutions, including accepting a static scene, dashboard, runnable shell, or geometric blockout as a finished game.

General projects use the same evidence engine with domain-appropriate product and quality contracts.

## Controlled Fan-out

Fan-out is an accelerator, not a ceremony.

Parallelize work only when outputs are independently judgeable, isolated in ownership, faster in parallel, and mergeable under one lead. Good candidates include isolated asset families, read-only research, independent tests, audio, bounded UI surfaces, and performance profiling.

Keep product identity, core loop, shared game state, architecture, global lighting or post-processing, final composition, integration, and final approval under one owner when coupled.

> Fan out work, not competing interpretations of the game.

### No-idle scheduling

For non-trivial Fan-out, LoopSeed records a small `task-graph.json` and derives the maximum safe runnable batch. Relations are explicit:

- `HARD_DEPENDENCY` blocks only its direct consumer;
- `SOFT_ADVICE` never blocks builders;
- `INDEPENDENT` permits concurrent work when ownership is isolated.

Joins choose `FIRST_SUCCESS`, `QUORUM`, or `ALL_REQUIRED`. Waiting is refused while any safe runnable task remains. Shared write scopes serialize; separate worktrees can proceed concurrently. The Lead keeps scheduling responsibility after delegation.

## Evidence-governed completion

After the brief is locked:

```text
BIND → PLAN → IMPLEMENT → VERIFY
                       FAIL ↓    ↓ PASS
                          REPAIR → VERIFY → FINALIZE
```

- acceptance is declared before substantial implementation;
- a builder cannot approve its own gate;
- failed gates must be repaired and reverified;
- two no-progress rounds force root-cause replanning;
- open P0/P1 defects block completion;
- only the finalizer can write `VERIFIED`;
- `BLOCKED` requires an exact external blocker and exact unblock condition;
- low quality, a failing test, or an exhausted first route are repair signals, not excuses to stop.

### Integrity Bridge

After implementation, LoopSeed freezes a separate `verification_binding` for the real Git HEAD and one stable deliverable artifact. Bind only after committing candidate and verifier source: tracked product content must match HEAD, and non-ignored untracked content must be the bound deliverable or a current hashed evidence artifact. `.loopseed` control data and Git-ignored environment/build content are outside that candidate-cleanliness check, so verification must not depend on mutable ignored source.

Machine gates run their commands through the evidence runner, which records exit code, timeout, bounded output, HEAD, tracked/untracked cleanliness, and artifact SHA-256 before and after execution. Independent gate commands may run in parallel; their receipts merge under a short project transaction. Human or visual PASS gates must point to an existing screenshot, recording, or report that is hashed when recorded. A command merely written into prose is never execution evidence.

If repair changes the candidate, a new binding generation archives the old subject and resets its old gate passes. Required tasks must be `SUCCEEDED`; every optional task must also be explicitly settled, normally `CANCELLED` when a candidate is discarded.

## Control plane

```text
.loopseed/one-shotted/
├── project-identity.md
├── architecture-contract.md
├── goal-contract.json
├── creative-brief.json
├── compiled-shot.md          # after the creative lock
├── dialogue.jsonl
├── acceptance.json
├── expert-registry.json
├── task-graph.json
├── state.json
├── evidence.jsonl
├── defects.jsonl
└── final-report.json         # only after successful finalization
```

The control plane stores compact decisions and evidence, never private reasoning or secrets.

## Add and verify a gate

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . \
  --id FLOW \
  --title "Complete game loop" \
  --criterion "A fresh player can complete, fail, and restart the documented slice" \
  --owner lead \
  --verifier verifier \
  --machine

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition \
  --root . --phase PLAN --next "Plan the bounded implementation"
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition \
  --root . --phase IMPLEMENT --next "Build and commit the candidate"

# Run the project-specific build, then commit candidate and verifier source.
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition \
  --root . --phase VERIFY --next "Freeze and verify the candidate"

head="$(git rev-parse HEAD)"
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py bind \
  --root . \
  --project "my-game" \
  --candidate "$head" \
  --artifact build/game.zip

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py run-evidence \
  --root . \
  --gate FLOW \
  --actor verifier \
  --command "python tools/playtest.py" \
  --project "my-game" \
  --candidate "$head" \
  --artifact build/game.zip
```

For a human or visual gate, use `record --artifact captures/flow-pass.mp4`; the file must exist inside the project and remains hash-checked through finalization.

### Upgrade from v0.7

- An ACTIVE v0.7 run may continue. Its first v0.7.1 `bind` resets pre-binding PASS claims, then the verifier must rerun them with `run-evidence` or hashed artifacts.
- `record --command` is intentionally rejected because it never executed the command. Use `bind` plus `run-evidence`.
- For a legacy cancelled `FIRST_SUCCESS`/`QUORUM` arm that was implicitly required, run `task-requirement --task <ID> --optional --actor lead --summary "legacy candidate arm"`.
- A v0.7 run already marked `VERIFIED` remains a legacy, unattested historical receipt. Start a fresh run if a v0.7.1 integrity receipt is required; terminal history is not silently re-signed.

## Finalize

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py finalize --root .
```

Finalization fails closed unless the creative lock is valid, the verification binding is current, every required task is `SUCCEEDED`, every optional task is explicitly settled, at least one required gate exists, every required gate has real machine or hashed-artifact PASS evidence, contracts are consistent, and no P0/P1 defect is open. The terminal report is then cross-checked against the current run, gates, evidence, tasks, binding, and timestamp.

See [One-Shotted Mode](skills/loopseed/references/one-shotted-mode.md) for the complete workflow.

## Why this is not a giant agent framework

LoopSeed minimizes coordination rather than maximizing agent count.

- Focused uses the minimum useful topology.
- Studio activates only the production disciplines required by the slice.
- Moonshot fans out independent quality surfaces but keeps one game identity and one integration owner.
- The scheduler maximizes safe runnable work, not agent count, and forbids idle waits for soft advice.
- State is updated at decisions, evidence, route changes, blockers, and terminal results—not every thought or tool call.

## Validate locally

```bash
python -m json.tool .codex-plugin/plugin.json >/dev/null
find skills/loopseed/schemas skills/loopseed/templates -name '*.json' -print0 \
  | xargs -0 -n1 python -m json.tool >/dev/null
python -m compileall -q hooks skills/loopseed/scripts tests
python -m unittest discover -s tests -v
```

## Core references

- [One-Shotted mode](skills/loopseed/references/one-shotted-mode.md)
- [State contracts](skills/loopseed/references/state-contract.md)
- [Runtime ladder](skills/loopseed/references/runtime-ladder.md)
- [Playbook](skills/loopseed/references/playbook.md)

## License

MIT. See [LICENSE](LICENSE).
