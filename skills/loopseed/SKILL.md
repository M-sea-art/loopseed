---
name: loopseed
description: Run a game-first, dialogue-calibrated, evidence-governed production loop from an explicit `$loopseed` goal. Use `$loopseed one-shotted` followed by a goal when one authorization should launch autonomous planning, controlled fan-out, implementation, independent verification, repair, and fail-closed finalization.
---

# LoopSeed

Use only after an explicit `$loopseed` invocation. Never infer activation from similar wording or an old state file.

LoopSeed is a **game-first AI production engine**. It can also run general software and product work through a lighter domain adapter.

Its operating idea is:

```text
creative dialogue aims the shot
        ↓
One-Shot authorization ignites production
        ↓
controlled Fan-out accelerates independent work
        ↓
no-idle scheduling keeps every safe node moving
        ↓
evidence decides whether the result is complete
```

LoopSeed has two operating modes:

- **Standard:** `$loopseed <goal>` — the smallest useful Explore → Act → Observe → Verify → Adapt loop.
- **One-Shotted:** `$loopseed one-shotted <goal>` — one human authorization starts a durable, contract-bound production run.

“One-Shotted” means **one production authorization**, not necessarily one user message and not one model response. A game idea may first be calibrated through multiple creative dialogue rounds. Once the user-authorized creative brief is locked, production proceeds without repeated prompting.

## Shared authority

Bind one root goal and acceptance to this order:

1. the user's explicit current instruction and accepted dialogue decisions;
2. the locked creative brief and compiled shot;
3. named project plans, milestones, product specifications, and reference files;
4. repository instructions such as `AGENTS.md`;
5. tests and the running product as evidence.

Existing implementation is evidence, not authority when it conflicts with the intended product.

## Standard mode

Use the cheapest loop that can close the goal:

1. **Explore** the closest real state and highest-value unknown.
2. **Act** with the smallest coherent authorized change.
3. **Observe** the running path, tests, UI, screenshots, artifacts, or source output.
4. **Verify** against the same acceptance conditions.
5. **Adapt** by repairing the cause or choosing a materially different route.

Default to one main thread, one writer, and one integration path. Delegate only independent work whose expected value exceeds coordination and token cost. Create `.loopseed.md` only when durable relay is actually needed.

## One-Shotted activation

Initialize from the target project root:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py init \
  --root . \
  --goal "<goal>"
```

Optional controls:

```text
--domain auto|game|general
--production-mode auto|focused|studio|moonshot
--dialogue auto|on|off
--max-dialogue-rounds 1..8
```

Defaults:

- a detected **game** goal enters `CALIBRATE` with creative dialogue enabled;
- a **general** goal enters `BIND` on the focused path unless dialogue or Moonshot is explicitly requested;
- a clear game goal may use `--dialogue off`, but only when product identity, experience, artifact, stage, and acceptance are already unambiguous.

## Creative co-director dialogue

During `CALIBRATE`, do not behave like a requirements questionnaire. Treat the user's idea as a seed to be continued.

The model may:

- **preserve** the idea's identity and accepted decisions;
- **clarify** material ambiguity;
- **correct** contradictions while explaining the tradeoff;
- **amplify** the strongest experience or differentiator;
- **complete** missing product logic;
- **continue** ideas already accepted by the user;
- **offer options** when a real product choice remains.

Every model turn must advance at least one material decision surface. A question must offer **two to four meaningfully different options**, recommend one, and state the consequence of each. Options may be blended when the user explicitly combines them.

Do not:

- repeat a question already answered;
- ask for facts available in the repository;
- ask low-level reversible implementation questions;
- silently replace the user's game with an easier product;
- lower ambition merely to simplify implementation;
- continue interviewing after the shot is precise enough to compile.

The default dialogue cap is five model question rounds. It is a ceiling, not a target. Stop earlier when the brief is ready. At the cap, synthesize the strongest recommendation and seek the final material decision rather than opening another discovery loop.

Record dialogue decisions with:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py dialogue-turn \
  --root . \
  --actor model \
  --kind question \
  --summary "Choose how the first slice proves the world is alive" \
  --effect preserve \
  --effect amplify \
  --advance core_loop \
  --advance hero_moment \
  --option "A|Three-day crisis|A compact complete management loop" \
  --option "B|Cinematic scene|More spectacle but weaker gameplay proof" \
  --recommended A
```

User answers and decisions are recorded in the same ledger. Dialogue is not production authorization until the accepted decisions are compiled and locked.

## Production modes

- **Focused** — complete the smallest coherent result quickly; do not expand the product idea.
- **Studio** — the default game-production target: a coherent, presentation-ready vertical slice with game feel, art direction, asset, playtest, and performance contracts.
- **Moonshot** — deliberately amplify the strongest experience and use aggressive but bounded fan-out. Moonshot must state both an ambition expansion and a scope guard.

Moonshot means **raise the experiential ceiling, not multiply features without limit**. Ambition may exceed the final evidence; the verdict may not.

## Creative brief lock

Before leaving `CALIBRATE`, compile one user-authorized creative brief containing at least:

- seed intent and product outcome;
- preserved ideas, explicit revisions, and amplifications;
- North Star and must-not-lose rules;
- bounded scope and non-goals;
- production mode;
- reference roles;
- required evidence;
- for games: player promise, player role, core loop, world response, unique hook, art direction, game feel, hero moment, vertical slice, asset strategy, and performance budget;
- the user answer or decision that authorizes the lock.

Lock it with:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py lock-brief \
  --root . \
  --file creative-brief.json
```

This writes a stable `creative-brief.json` and human-readable `compiled-shot.md`, then moves the run to `BIND`. A normal phase transition cannot bypass this lock, and production acceptance gates cannot be declared while dialogue is still open.

## One-Shotted production

After the creative brief is locked:

For an ACTIVE v0.7 run, migrate in the background without a new user question: preserve the creative lock, let the first v0.7.1 binding reset legacy PASS claims, infer machine gates from old command claims, explicitly mark disposable cancelled arms optional, and rerun evidence. Never present an old terminal v0.7 receipt as v0.7.1-attested.

1. freeze Project Binding, Artifact Contract, and Stage Target from the compiled shot;
2. declare observable acceptance gates in `BIND` or `PLAN`, before substantial implementation;
3. assign each gate an implementation owner and a different verifier;
4. plan the smallest complete route that satisfies the chosen production mode;
5. record non-trivial work in `task-graph.json`; classify every relation as `HARD_DEPENDENCY`, `SOFT_ADVICE`, or `INDEPENDENT`;
6. dispatch every safe runnable node before waiting; use `FIRST_SUCCESS`, `QUORUM`, or `ALL_REQUIRED` only at explicit joins;
7. fan out only independently judgeable work with clean ownership and shared integrity references;
8. keep coupled game identity, core loop, shared runtime state, architecture, composition, and final integration under one owner;
9. merge into one product, run whole-product criticism, repair failures, and reverify;
10. commit candidate and verifier source, then in `VERIFY` freeze the clean real Git HEAD and stable deliverable as `verification_binding`;
11. execute machine gates with `run-evidence`; hash screenshots, recordings, or reports for human gates;
12. finalize only when required tasks succeeded, optional tasks are explicitly settled, and the terminal receipt cross-validates.

## No-idle scheduling

The Lead always retains scheduling responsibility after delegation. A specialist response is advice unless a named consumer truly cannot proceed without it.

- `HARD_DEPENDENCY` blocks only its direct consumer.
- `SOFT_ADVICE` never blocks execution; merge it at the next safe checkpoint.
- `INDEPENDENT` explicitly permits concurrent progress when write ownership is safe.
- A shared write scope has one writer. Separate worktrees or isolation boundaries may run overlapping scopes concurrently.
- Before waiting, run the scheduler with the current surface's available subagent capacity when known. Waiting is legal only when no safe runnable node remains, the named tasks are already running, and a fallback is recorded.
- If a task becomes runnable while a wait is declared, validation fails with `NO_IDLE_WHILE_RUNNABLE`.

Use the bundled `add-task`, `task-status`, `schedule`, and `wait` commands for non-trivial Fan-out. Small Focused work may remain on the main thread without ceremonial task entries.

State machine:

```text
CALIBRATE → BIND → PLAN → IMPLEMENT → VERIFY
                                  FAIL ↓    ↓ PASS
                                     REPAIR → VERIFY → FINALIZE
```

## Game-first production contract

For game projects, automatically reason about and verify the relevant subset of:

- player promise and first-minute understanding;
- complete core loop, success, failure, and restart;
- input response, camera, animation, sound, feedback, and game feel;
- Art Bible, silhouette, materials, lighting, composition, and UI/world coherence;
- asset provenance, placeholder replacement, animation, audio, and licensing;
- fixed shots, isolated subject review, scripted playtest, and complete-flow evidence;
- FPS, frame time, draw calls, triangles, memory, load time, build, package, and relaunch;
- the prohibition against accepting a blockout, static scene, or runnable shell as finished game production.

General projects use the same evidence engine with domain-appropriate product, flow, artifact, quality, and performance gates.

## One-Shotted invariants

- One lead owns creative integrity and final integration.
- Delegation never transfers the Lead's scheduling responsibility.
- Fan out work, not product identity or competing interpretations of the brief.
- Parallel writers require isolation; coupled concerns stay sequential.
- A runnable task forbids waiting; soft advice is never a global approval gate.
- Waiting requires an explicit dependency or join, named running tasks, and a fallback.
- A worker cannot approve its own gate.
- A failed gate moves the run to `REPAIR`; repair must be reverified.
- A repaired candidate receives a new verification-binding generation; old gate passes reset.
- Required tasks must end `SUCCEEDED`; disposable `FIRST_SUCCESS` or `QUORUM` candidate arms are optional and end `CANCELLED` when discarded.
- Bind rejects tracked candidate drift and non-ignored untracked content outside the bound/current evidence artifacts; `.loopseed` is control data, not candidate source.
- A command string is not evidence unless `run-evidence` executed it without timeout against the bound HEAD, clean candidate content, and artifact.
- Human or visual PASS evidence names at least one real project-local artifact whose SHA-256 remains stable.
- Keep only changes that preserve already-passed gates; otherwise repair or roll back.
- Two no-progress rounds force root-cause replanning and a materially different route.
- Only the finalizer may write `VERIFIED`.
- `BLOCKED` requires the exact missing external condition and exact unblock condition, with no runnable or running internal task.
- State and prose are control signals, never completion proof.
- Do not fan out agents ceremonially. Use the chosen mode to determine the minimum useful topology.

## Terminal states

- `VERIFIED` — every required task succeeded, every optional task settled, every required gate has current bound evidence, the terminal receipt cross-validates, and no open P0/P1 defect remains.
- `BLOCKED` — an exact, irreplaceable external gate prevents further safe progress and has a stated unblock condition.
- `ABORTED` — the owner explicitly stops the run.

Failure, low quality, a failing test, uncertainty, or an exhausted first route are not blockers. They trigger repair, rollback, or replanning.

## Reporting

At the end, report only:

- terminal verdict;
- direct evidence and final report path;
- changed scope;
- remaining non-blocking risk;
- exact unblock condition when blocked.

An ordinary LoopSeed invocation does not authorize changing LoopSeed itself.
