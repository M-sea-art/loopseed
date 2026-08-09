# One-Shotted Mode

One-Shotted mode turns **one production authorization** into a bounded autonomous completion run.

For games, the authorization may be preceded by a short or multi-round creative co-director dialogue. The dialogue aims the shot; it does not split production into repeated human approvals.

```text
player seed
    ↓
creative co-director dialogue
preserve · correct · amplify · complete · continue · offer options
    ↓
user-authorized creative brief
    ↓
One-Shot production lock
    ↓
controlled Fan-out + integration
    ↓
repeatable evidence + independent verifier
    ↓
PASS → preserve / FAIL → repair or rollback
    ↓
final gate decides completion
```

## Product position

LoopSeed is game-first. Its primary job is to turn a player's game idea into a coherent production brief, then rapidly organize design, engineering, assets, integration, playtesting, and verification.

General software projects use the same evidence-governed engine with a lighter product adapter.

## Invocation

```text
$loopseed one-shotted <natural-language goal>
```

Initialize the project-local control plane:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py init \
  --root . \
  --goal "<the user's seed>"
```

Optional controls:

```text
--domain auto|game|general
--production-mode auto|focused|studio|moonshot
--dialogue auto|on|off
--max-dialogue-rounds 1..8
```

The default game route enters `CALIBRATE`. The default general route enters `BIND`. A clear game contract may explicitly skip dialogue; Moonshot always benefits from an explicit ambition and scope calibration.

## What the creative dialogue is for

The user is not required to arrive with a finished design document. The model acts as a co-director that can:

- preserve the idea's identity;
- identify and explain contradictions;
- correct a weak or conflicting formulation without erasing the original intent;
- amplify the most distinctive player experience;
- complete missing game logic;
- continue concepts the user already accepted;
- present two to four meaningful options with a recommendation and consequences.

A dialogue round is justified only when it advances a material surface such as:

- player promise or role;
- core loop and world response;
- unique hook;
- target artifact and production stage;
- art direction, game feel, asset route, or hero moment;
- vertical-slice boundary;
- performance or evidence contract;
- production mode;
- an irreversible technical or commercial choice.

Do not ask for repository facts, reversible implementation details, cosmetic trivia, or decisions already made. Do not reset accepted ideas in later rounds.

## Dialogue turns

Model questions require two to four options and one recommendation:

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
  --option "B|Cinematic scene|More spectacle but weaker gameplay evidence" \
  --option "C|Large sandbox|More breadth but lower completion confidence" \
  --recommended A
```

Record the user's natural-language response:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py dialogue-turn \
  --root . \
  --actor user \
  --kind answer \
  --summary "Use A, but preserve the inherited-memory idea and the high-fidelity cutaway view"
```

The ledger stores compact decisions, not private reasoning or full transcripts.

## Dialogue stopping rule

The default maximum is five model question rounds. It is a ceiling, not a quota.

Lock the shot as soon as all of the following are sufficiently resolved:

- the product identity is stable;
- the player promise and core experience are clear;
- the first complete production boundary is chosen;
- the user has accepted or combined the material options;
- must-not-lose rules and forbidden substitutions are explicit;
- the selected mode is clear;
- evidence can decide success or failure.

Do not ask another question merely to appear thorough. If the cap is reached, present the strongest synthesis and the remaining material decision rather than starting a new discovery branch.

## Production modes

### Focused

Use the smallest topology and scope that can finish one coherent result quickly. Preserve the requested product; do not volunteer additional systems.

### Studio

Default game-production route. Produce a coherent, presentation-ready vertical slice with game identity, Art Bible, game feel, assets, complete flow, playtest, and performance evidence.

### Moonshot

Amplify the most compelling experience and use aggressive but bounded Fan-out. Moonshot requires:

- an explicit ambition expansion;
- an explicit scope guard;
- at least one documented amplification of the user's seed;
- the same fail-closed evidence rules as every other mode.

Moonshot deepens the strongest experience. It does not authorize uncontrolled feature multiplication or inflated completion claims.

## Creative brief

The dialogue compiles into `creative-brief.json` and `compiled-shot.md`.

For a game, the brief includes:

- seed intent and product outcome;
- North Star;
- original and preserved ideas;
- visible revisions and amplifications;
- decisions, bounded scope, non-goals, and must-not-lose rules;
- player promise and role;
- core loop and world response;
- unique hook;
- art direction and game feel;
- hero moment and vertical slice;
- asset strategy and performance budget;
- reference roles;
- required evidence;
- the user answer or decision that authorizes the production lock.

Lock it with:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py lock-brief \
  --root . \
  --file creative-brief.json
```

The lock moves `CALIBRATE → BIND`. Ordinary transitions cannot bypass it. Acceptance gates cannot be added while calibration is open.

## Control plane

The initialized run contains:

```text
.loopseed/one-shotted/
├── project-identity.md
├── architecture-contract.md
├── goal-contract.json
├── creative-brief.json
├── compiled-shot.md          # after creative lock
├── dialogue.jsonl
├── acceptance.json
├── expert-registry.json
├── task-graph.json
├── state.json
├── evidence.jsonl
├── defects.jsonl
└── final-report.json         # only after successful finalization
```

This is a small production control surface, not a work diary. Never store secrets, private reasoning, or copied source dumps.

## State machine

```text
CALIBRATE
  co-direct the seed and lock the user-authorized brief
    ↓
BIND
  freeze project, artifact, and stage identity
    ↓
PLAN
  choose the smallest complete route, dependency kinds, ownership, and joins
    ↓
IMPLEMENT
  execute; fan out only independently judgeable work
    ↓
VERIFY
  independent verifier runs the real gates
    ├── PASS → next gate or FINALIZE
    └── FAIL → REPAIR
                 ↓
               IMPLEMENT / VERIFY
```

Two no-progress rounds during calibration force a concise synthesis and final option decision. Two no-progress production rounds force root-cause replanning and a materially different route.

## Game-first contracts

Use the relevant subset of these contracts:

### Game identity

- player promise;
- player role;
- repeated player action;
- world response;
- unique hook;
- why the result is a game rather than a static scene or interface.

### Game feel

- input latency and response;
- camera behavior;
- movement, animation, hit or state feedback;
- sound and visual response;
- first-minute comprehension;
- success, failure, restart, and emotional rhythm.

### Art production

- Art Bible and palette;
- silhouette, material, lighting, scale, composition, and UI/world coherence;
- asset strategy and provenance;
- placeholder replacement boundary;
- fixed shots and isolated subject views;
- prohibition against approving a blockout as final art.

### Runtime and delivery

- complete scripted playthrough;
- production build, boot, package, relaunch, and state persistence where relevant;
- FPS, frame time, draw calls, triangles, memory, load time, and regression budgets;
- target hardware or an explicit degraded-observation boundary.

## Fan-out

The creative brief and integrity locks are shared by every worker. Fan out only when outputs are:

- independent;
- independently judgeable;
- isolated in write scope or worktree;
- faster in parallel than sequentially;
- mergeable under one lead.

Good candidates include isolated asset families, read-only investigations, independent tests, audio, bounded UI surfaces, and performance profiling.

Keep the following under one sequential owner when coupled:

- product identity;
- core loop and shared game state;
- architecture;
- lighting or post-processing ownership;
- final composition;
- integration;
- final approval.

Fan out work, not competing interpretations of the game.

### No-idle task graph

For non-trivial Fan-out, register bounded tasks after entering `PLAN`:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-task \
  --root . \
  --id R8-ARCH \
  --purpose "Inspect the slab material route" \
  --owner technical-architect \
  --read-only

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-task \
  --root . \
  --id R8-A \
  --purpose "Build isolated visual candidate A" \
  --owner builder-a \
  --relation R8-ARCH:SOFT_ADVICE \
  --write-scope Assets/_Game \
  --isolation worktree:r8-a
```

Relations mean:

- `HARD_DEPENDENCY` — the named task must satisfy this consumer's join policy;
- `SOFT_ADVICE` — useful input that never blocks the consumer;
- `INDEPENDENT` — explicit evidence that the tasks may proceed independently.

Hard dependencies use one explicit join:

- `ALL_REQUIRED` — every hard dependency succeeds;
- `FIRST_SUCCESS` — the first successful route releases the consumer;
- `QUORUM` — the declared number of successful routes releases the consumer.

Ask for the maximum safe batch, optionally bounded by the available subagent capacity:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py schedule \
  --root . \
  --capacity 4
```

Pass the actual available subagent capacity when the surface exposes it; otherwise use the smallest profitable batch and reschedule as slots open. The scheduler derives readiness, respects shared write scopes, and permits overlapping scopes only across different isolation boundaries such as separate worktrees. Mark each task `RUNNING`, `SUCCEEDED`, `FAILED`, `BLOCKED`, or `CANCELLED` with `task-status`.

Every task is required unless added with `--optional`. Finalization accepts required tasks only as `SUCCEEDED`, and every optional task must also leave `PENDING`, `RUNNING`, `FAILED`, or `BLOCKED`; discarded arms end `CANCELLED`. For `FIRST_SUCCESS` or `QUORUM`, declare disposable candidate arms optional and keep the merge or consumer task required.

To migrate a v0.7 arm that was cancelled before optionality was explicit:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py task-requirement \
  --root . \
  --task CANDIDATE-B \
  --optional \
  --actor lead \
  --summary "Legacy disposable candidate arm"
```

Before using a platform wait mechanism, declare the rendezvous:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py wait \
  --root . \
  --for R8-A \
  --reason JOIN \
  --fallback "continue with the best completed candidate or replan the failed route"
```

The command refuses to wait if any safe runnable task remains. A technical director, critic, or other advisor is `SOFT_ADVICE` unless a direct consumer has a real hard dependency on its output. Delegation never transfers scheduling responsibility away from the Lead.

## Acceptance gates

A gate names:

- a stable ID;
- one observable criterion;
- whether it is required;
- an implementation owner;
- a different verifier;
- evidence IDs;
- status: `PENDING`, `PASS`, `FAIL`, or `BLOCKED`.

Example:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . \
  --id FLOW \
  --title "Complete game loop" \
  --criterion "A fresh player can complete, fail, and restart the documented slice" \
  --owner lead \
  --verifier verifier \
  --machine
```

Choose gates close to the real product. Do not replace player experience with build-only checks.

## Independent evidence

After the candidate is built and the run is in `VERIFY`, commit candidate and verifier source, then freeze the actual Git HEAD and one stable deliverable artifact:

```bash
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

`bind` and `run-evidence` reject tracked product/verifier changes relative to HEAD. Non-ignored untracked content must be inside the bound artifact or a current, still-matching hashed evidence artifact. `.loopseed` control state and Git-ignored environment/build content are excluded; do not place mutable source that affects verification behind Git ignore rules.

`run-evidence` is the only command path that treats a command as executed. It preserves the supplied shell command, records exit code, timeout, bounded stdout/stderr, Git HEAD, tracked/untracked cleanliness, and artifact identity before and after execution. A PASS requires exit code zero, no timeout, and a stable binding. Independent gates may execute concurrently; receipt commits merge under a short project-local transaction, while bind/finalize wait for active verifier commands.

The bridge proves observed command/HEAD/artifact/ledger consistency and fails closed on mismatches. Plain project-local JSON cannot cryptographically authenticate a human or agent identity against an attacker who can rewrite the whole control plane; deployments needing that guarantee must add externally signed runner/verifier receipts.

For a human or visual gate, use `record --artifact <screenshot-or-recording>`. PASS requires at least one existing project-local artifact and stores its SHA-256. Only the latest current-generation event decides a gate, so a fresh artifact PASS can supersede a stale rejected capture. A `FAIL` moves the run to `REPAIR`. Repair must be rerun by the verifier. If repair changes the candidate, return to `VERIFY` and bind a new generation; the ledger boundary advances and old gate passes are reset.

### v0.7 migration

The first v0.7.1 binding on an ACTIVE v0.7 run treats earlier PASS claims as legacy/unattested, clears their gate references, and requires fresh evidence. Old `record --command` invocations must be rerun with `run-evidence`. An already terminal v0.7 `VERIFIED` report stays historical and cannot be silently upgraded; start a fresh run when a v0.7.1 integrity receipt is required. The published v1.2 evidence schemas describe new receipts; legacy pre-binding ledger rows remain readable only as unattested history.

## Defects

Append compact defect events:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py defect \
  --root . \
  --id VIS-001 \
  --severity P1 \
  --status OPEN \
  --summary "Primary game state is visually unreadable" \
  --actor verifier
```

Resolve with another event using the same ID and `--status RESOLVED`. Open P0/P1 defects prevent finalization.

## Completion

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py finalize --root .
```

Finalization fails closed unless:

- the creative brief is locked when calibration is enabled;
- at least one required gate exists;
- every required gate is `PASS`;
- each PASS references current-generation machine evidence or verifier-authored hashed artifact evidence;
- a real Git verification binding still matches the candidate HEAD and artifact SHA-256;
- every required task is `SUCCEEDED`;
- every optional task has an explicit `SUCCEEDED` or `CANCELLED` disposition;
- no P0/P1 defect remains open;
- contracts and ledgers are internally consistent;
- `final-report.json` matches the current run, gates, evidence, tasks, binding, and timestamp.

Successful finalization writes `final-report.json` and sets `VERIFIED`.

## Economy rules

- Dialogue rounds must buy precision, not ceremony.
- One production authorization does not imply maximal Fan-out.
- Maximum parallel efficiency means the largest safe runnable batch, not the largest possible agent count.
- Never idle for advice while an independent builder, test, probe, or integration preparation task can run.
- Focused uses the minimum useful topology.
- Studio activates only the disciplines required by the slice.
- Moonshot accelerates independent quality surfaces but remains bounded.
- Reuse the project's build, runtime, capture, and test harnesses before adding orchestration.
- Prefer the closest real acceptance test over long status reports.
