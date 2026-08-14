# Agent-Native Game Development Stack v1

Status: FOUNDATION CANDIDATE

This document defines the first thin-waist architecture for turning LoopSeed into the control plane of a broader agent-native game-development stack without turning LoopSeed itself into a giant engine, asset system, or visual framework.

## One-line definition

Agent-Native Game Development Stack is infrastructure that lets agents recover project intent, compile a bounded production plan, discover specialist capabilities, make and run the real game, observe it directly, challenge weak output with evidence, and convert expensive failures into reusable capabilities.

## Architectural rule

Keep responsibilities separate:

- LoopSeed owns project truth, planning recovery, production governance, scheduling, evidence binding, defects, and finalization.
- Gauntlet Loop owns local quality convergence: bar, observation, challenger, fresh critic, biggest gap, bounded repair, freeze/rollback/reset.
- Engine adapters such as Godot AI own engine inspection and manipulation, not product direction.
- World/geometry systems own world-plan compilation, geometry, navigation/proxy facts, and structural audits.
- Asset compilers own bounded asset specifications, generation/compilation, multi-view QA, deterministic validation, and engine-ready exports.
- Harnesses own capture, playtest, visual diagnostics, regression, geometry checks, and performance measurement.
- Capability Harvest turns validated production lessons into reusable skills, macros, templates, tests, tools, invariants, or knowledge.

No subsystem may approve its own final completion claim.

## Stack layers

```text
L0  Project Truth / Context Recovery
L1  Product + Creative Contract
L2  Director / Orchestration
L3  Engine Plane
L4  World Plane
L5  Asset Plane
L6  Observability / Proof Harness
L7  Quality Ratchet
L8  Evidence / Finalization
L9  Capability Harvest / Learning
```

LoopSeed remains the L0/L1/L2/L8 control plane. Gauntlet remains an independently invokable L7 quality ratchet. Other repositories and tools plug into the stack as capabilities.

## v1 foundation contracts

This branch introduces three engine-neutral contracts.

### 1. Capability Registry

A capability is a discoverable operation the Director can route to rather than relying on conversational memory.

Examples:

- `godot.scene.inspect`
- `godot.runtime.capture`
- `wuxia.asset.compile`
- `wuxia.eave.curved-v2`
- `threejs.archkit.profile-loft`
- `qa.visual.fixed-camera`
- `qa.performance.frame-distribution`

Each capability records its provider, domain, inputs, outputs, engine support, required tools, evidence expectations, ownership scope, cost class, fallback, status, and provenance.

The registry is not project truth. It describes what the production system knows how to do.

### 2. WorldPlan

WorldPlan is an engine-neutral source of truth for stable spatial and semantic facts that multiple systems must agree on.

It can describe:

- camera contracts;
- semantic locations and transforms;
- routes and chokepoints;
- build slots;
- gameplay proxies;
- invariants;
- engine-specific adapter notes.

The same WorldPlan may be consumed by Three.js visualization, Godot runtime construction, Blender/world compilation, navigation checks, and QA tooling.

A WorldPlan must not become a replacement for engine scene files. It owns shared facts, not every implementation detail.

### 3. Capability Harvest

A failed or difficult production round should be classified before it disappears into history.

```text
one_off_defect     -> repair only
invariant          -> durable rule
skill              -> repeatable agent workflow
g eometry_macro     -> reusable geometry operation
template_gap        -> compiler/factory capability missing
tool_gap            -> missing executable operation
test_gap            -> QA blind spot
knowledge_gap       -> durable domain knowledge
architecture_gap    -> systemic design limitation
structural_reset    -> current route is no longer rational
```

Capability Harvest does not automatically promote every lesson into infrastructure. It records the evidence and proposed next action so a later engineering pass can decide whether promotion is justified.

## Minimal CLI

The foundation CLI lives at:

`skills/loopseed/scripts/agent_native_stack.py`

Initialize local stack state:

```bash
python skills/loopseed/scripts/agent_native_stack.py init --root . --world-id my-game
```

This creates:

```text
.loopseed/agent-native-stack-v1/
  capability-registry.json
  world-plan.json
  harvest.jsonl
```

Register a capability:

```bash
python skills/loopseed/scripts/agent_native_stack.py register-capability \
  --root . \
  --id godot.runtime.capture \
  --domain engine \
  --provider godot-ai \
  --description "Capture observable runtime evidence from the live Godot project" \
  --engine godot \
  --output screenshot \
  --evidence runtime-artifact \
  --ownership isolated \
  --status experimental
```

Record a harvested production lesson:

```bash
python skills/loopseed/scripts/agent_native_stack.py harvest \
  --root . \
  --source "visual gate ROOF-02" \
  --kind template_gap \
  --summary "Existing roof factory cannot express the required asymmetric upward eave tension" \
  --evidence captures/roof-02-fail.png \
  --capability-id wuxia.eave.curved-v2 \
  --next-action "Implement and verify a reusable curved-eave factory"
```

List registered capabilities:

```bash
python skills/loopseed/scripts/agent_native_stack.py list-capabilities --root .
```

## First production target

The recommended first real consumer is the wuxia sect-management project because it exercises all three contracts:

- WorldPlan: fixed camera, K0/K1/K2 gates, courtyards, stairs, build slots, main route, enemy route, visual shell and gameplay proxies.
- Capability Registry: Godot AI operations, Three.js world/geometry experiments, Blender/Wuxia Asset Compiler operations, visual QA and performance harnesses.
- Capability Harvest: every repeated visual/geometry failure can become a rule, macro, factory, test, or template gap instead of another one-off patch.

## What v1 deliberately does not do yet

- It does not merge Gauntlet into LoopSeed.
- It does not copy external repositories into LoopSeed.
- It does not define a universal geometry engine.
- It does not auto-promote harvested lessons into code.
- It does not claim that a registered capability is verified unless its own evidence exists.
- It does not replace project-specific GDD, creative brief, engine scenes, asset specs, or runtime tests.

## Next implementation slices

1. Add capability discovery/routing from LoopSeed task planning.
2. Add schema validation and migration for local stack state.
3. Define the first wuxia `sect.world.json` and adapters for Three.js + Godot.
4. Build a deterministic game capture manifest: camera, seed/state, freeze, viewport, passes.
5. Connect Gauntlet verdicts and LoopSeed defects to Capability Harvest.
6. Add promotion gates so repeated harvest entries can become verified capability-registry entries.
7. Validate the full loop on one real vertical slice rather than a synthetic demo.

The governing principle is simple: production should leave the system more capable than it found it, but only when evidence justifies the new capability.
