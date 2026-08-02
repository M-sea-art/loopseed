# LOOPSEED Game-First Dialogue Engine v0.5.0

## Goal

Turn an unfinished player idea into one precise, ambitious, executable production shot without losing One-Shot speed.

```text
creative seed
    ↓
multi-round co-director dialogue
    ↓
locked creative brief
    ↓
Project Binding + Artifact Contract + Stage Target
    ↓
One-Shot production + controlled Fan-out
    ↓
merge + critic + repair + verification
```

The core hypothesis is:

> Multi-round dialogue creates precision; One-Shot and controlled Fan-out create rapid production; evidence keeps both honest.

LoopSeed is game-first. General projects retain the same evidence-governed runtime through a lighter adapter.

## Why v0.5 exists

The previous calibration protocol allowed at most one question round. That was useful for resolving a narrow ambiguity, but insufficient for creative game development where the user's seed may need to be:

- preserved across several decisions;
- corrected when two ideas conflict;
- amplified around the strongest player experience;
- completed into an actual game shape;
- continued rather than reset in each response;
- explored through a small number of meaningful options.

At the other extreme, an open-ended requirements interview would destroy One-Shot speed.

v0.5 therefore adds an executable `CALIBRATE` phase with a bounded, progressive, option-rich dialogue ledger and a user-authorized creative brief lock.

## Product definition

LoopSeed is:

> A game-first AI production engine that co-directs the player's idea until the shot is precise, then launches an uninterrupted production run with controlled Fan-out and evidence-governed completion.

It is not:

- a generic questionnaire;
- a giant multi-agent framework;
- a static prompt library;
- a game generator that accepts its own screenshots as proof;
- an excuse to turn a requested game into a blockout, dashboard, scene, or runnable shell.

## One-Shot definition

One-Shot means:

> one user-authorized production run after creative alignment is locked.

It does not require:

- exactly one user message;
- exactly one model response;
- zero preproduction dialogue.

It does require:

- one stable seed-intent anchor;
- accumulated accepted decisions;
- a locked product identity and bounded slice;
- no repeated confirmation after the lock;
- uninterrupted planning, implementation, verification, and repair until a terminal evidence state.

## Routes

### Game default

```text
Seed → CALIBRATE → creative lock → BIND → PLAN → IMPLEMENT → VERIFY
```

### General default

```text
Goal → BIND → PLAN → IMPLEMENT → VERIFY
```

### Explicit direct game shot

A game may skip dialogue only when the goal or existing project already makes the following unambiguous:

- game identity;
- player promise and core loop;
- target artifact and stage;
- bounded slice;
- must-not-lose rules;
- required evidence;
- absence of any material decision that would redirect the result.

Skipping dialogue is an optimization, not permission to blind-fire.

## Creative co-director behavior

The model may perform these visible operations:

| Operation | Meaning |
|---|---|
| Preserve | Retain original identity and accepted decisions |
| Clarify | Resolve a material ambiguity |
| Correct | Repair a contradiction while explaining the tradeoff |
| Amplify | Deepen the strongest player experience or differentiator |
| Complete | Add missing product logic without replacing identity |
| Continue | Extend an already accepted idea rather than resetting it |
| Offer options | Present meaningfully different paths when a real choice remains |

Every model turn must declare at least one operation and advance at least one material decision surface.

A question must:

- provide two to four meaningful options;
- recommend exactly one;
- state the material consequence of each;
- allow the user to combine or restate options in natural language.

The model must not:

- re-ask an answered question;
- forget accepted decisions;
- fall back to generic genre defaults after a specific idea is accepted;
- ask for repository facts or reversible engineering choices;
- silently lower ambition or replace the requested artifact;
- keep interviewing after the brief is ready.

## Dialogue rounds

Default maximum: **five model question rounds**.

Configurable range: **one to eight**.

This is a ceiling, not a quota. The dialogue can end after one or two rounds when ready.

Two no-progress rounds force the model to stop discovery, present the strongest current synthesis, expose only the remaining material choice, and move toward the lock.

At the configured maximum, the system must lock, explicitly block on an unresolved hard conflict, or present one final bounded decision. It may not open another discovery branch.

## Production modes

### Focused

- smallest complete result;
- fastest coherent route;
- no volunteered scope expansion;
- minimum useful topology.

### Studio

Default for games:

- coherent presentation-ready vertical slice;
- game identity and player promise;
- complete core loop;
- Art Bible and game feel;
- asset route and placeholder replacement;
- complete playtest;
- fixed visual evidence;
- performance budget.

### Moonshot

- deliberately amplifies the strongest experience;
- aggressively fans out independent quality surfaces;
- requires an ambition expansion;
- requires a scope guard;
- requires at least one explicit seed amplification;
- never lowers evidence standards.

Moonshot deepens the hero experience; it does not multiply features without bound.

## Creative brief

The dialogue compiles into:

```text
.loopseed/one-shotted/creative-brief.json
.loopseed/one-shotted/compiled-shot.md
```

Common required fields:

- seed intent;
- product outcome;
- North Star;
- original and preserved ideas;
- revisions and amplifications;
- decisions;
- bounded scope and non-goals;
- must-not-lose rules;
- reference roles;
- required evidence;
- production mode;
- user authorization event.

Game-specific fields:

- player promise;
- player role;
- core loop;
- world response;
- unique hook;
- art direction;
- game feel;
- hero moment;
- vertical slice;
- asset strategy;
- performance budget.

General-project fields:

- user job;
- primary flow;
- artifact type;
- target stage;
- success metrics.

Moonshot fields:

- ambition expansion;
- scope guard.

## Lock and authority

The user answer or decision referenced by the brief authorizes the production lock.

The lock:

- validates dialogue references;
- validates the domain and selected mode;
- requires at least one user event and one model synthesis/option event;
- writes the structured brief and human-readable compiled shot;
- freezes the accepted creative direction;
- moves `CALIBRATE → BIND`.

The lock cannot be bypassed by:

- a normal state transition;
- early acceptance-gate creation;
- a worker deciding that the user probably agrees;
- a verifier approving production direction.

Authority order after lock:

1. current user instruction and accepted dialogue decisions;
2. locked creative brief and compiled shot;
3. Project Binding, Artifact Contract, and Stage Target;
4. named project authority files;
5. approved implementation strategy;
6. transferable expert or benchmark principles;
7. worker proposals.

## Integrity locks

The creative brief is the human-readable production authority. It compiles into the existing integrity system rather than adding an unrelated orchestration framework.

After lock, freeze:

```text
project_binding_id
artifact_contract_id
stage_target_id
```

Every task, Fan-out worker, merge input, critic verdict, and final artifact must preserve those references and the creative brief ID.

## Game-first production contract

The compiler selects the relevant contracts from:

### Identity and experience

- player promise;
- player role;
- repeated action;
- world response;
- unique hook;
- first-minute comprehension;
- success, failure, restart, and emotional rhythm.

### Game feel

- input response;
- camera;
- movement and animation;
- hit or state feedback;
- sound;
- readable consequence;
- no dashboard substitution for embodied game experience.

### Art and assets

- Art Bible;
- palette, silhouette, material, lighting, scale, and composition;
- UI/world coherence;
- asset provenance and licenses;
- placeholder replacement boundary;
- fixed shots and isolated subject review;
- no blockout-as-final substitution.

### Runtime and delivery

- complete scripted playthrough;
- build, boot, package, relaunch, and persistence where relevant;
- FPS and frame-time distribution;
- draw calls and triangles;
- memory and load time;
- target-hardware identity;
- explicit degraded-observation boundary when the intended hardware is unavailable.

## Fan-out

Fan-out accelerates only after creative and production integrity are frozen.

Parallelize independently judgeable quality surfaces, not arbitrary folders or personas.

Possible parallel units:

- isolated asset families;
- audio;
- bounded UI surfaces;
- independent runtime or content tests;
- read-only investigations;
- performance profiling;
- alternative candidates that can be judged under the same contract.

Keep coupled surfaces sequential under one owner:

- game identity;
- core loop;
- shared game state;
- architecture;
- global lighting and post-processing;
- final composition;
- integration;
- final approval.

Each worker inherits unchanged:

- creative brief ID;
- project binding ID;
- artifact contract ID;
- stage target ID.

> Fan out work, not competing interpretations of the game.

## Verification

The final artifact is verified against the same locked intent and selected production mode.

Focused, Studio, and Moonshot change production strategy and ambition—not evidence truth.

A verifier may return:

- `PASS` when the direct gate evidence satisfies the contract;
- `FAIL` when a product or performance gate is missed;
- `BLOCKED` only when an exact external condition prevents further valid verification.

A beautiful screenshot cannot override a failed core loop or performance budget. A green build cannot approve unfinished art. A degraded software-renderer screenshot cannot be reported as native-GPU visual or FPS evidence.

## Protocol files

- `calibration-policy.yaml`
- `game-first-production-policy.yaml`
- `project-binding-schema.yaml`
- `artifact-contract-schema.yaml`
- `stage-awareness-policy.yaml`
- `expert-activation-policy.yaml`
- `task-graph-schema.yaml`
- `fanout-policy.yaml`
- `merge-contract.yaml`
- `critic-loop.yaml`
- `brand-trigger-schema.yaml`

## Benchmarks

- `benchmarks/oneshot-calibration.yaml`
- `benchmarks/wuxiang-zen-hall.yaml`
- `benchmarks/xuanmi-sect.yaml`
- `benchmarks/cross-project-contamination.yaml`

The calibration benchmark must prove:

- a clear general goal is not forced into dialogue;
- a game seed can advance over multiple rounds;
- accepted ideas survive later rounds;
- corrections and amplifications remain visible;
- every question has meaningful options and a recommendation;
- repeated questions are rejected;
- Studio and Moonshot compile different production strategies;
- Moonshot cannot lock without a scope guard;
- the creative lock requires a user answer or decision;
- production gates and phase transitions cannot bypass the lock;
- after lock, One-Shot execution begins without another confirmation.

## Success criteria

- the player can begin with a short, incomplete game idea;
- dialogue improves precision without becoming bureaucratic;
- the model may repair and enlarge ideas without erasing authorship;
- options expose real product consequences rather than cosmetic preferences;
- game projects receive game-specific production and evidence contracts;
- One-Shot execution begins once, after lock;
- controlled Fan-out makes production faster without fragmenting identity;
- completion remains fail-closed and evidence-bound;
- the same engine remains useful for general projects.
