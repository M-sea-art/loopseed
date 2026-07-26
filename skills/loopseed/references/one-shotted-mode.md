# One-Shotted Mode

One-Shotted mode turns **one human authorization** into a bounded autonomous completion run. It copies the successful engineering pattern behind strong “one-shot” agent projects without copying their domain or assuming that a single model response is enough.

## What is being replicated

The useful pattern is:

```text
one human goal
    ↓
project identity + architecture contract
    ↓
predeclared acceptance gates
    ↓
implementation owner(s)
    ↓
repeatable evidence harness
    ↓
independent verifier
    ↓
PASS → preserve / FAIL → repair or rollback
    ↓
final gate decides completion
```

The prompt is only the ignition. The architecture contract, ownership boundaries, deterministic or repeatable evidence, independent criticism, and honest stopping rule make the run self-driving.

## Invocation

```text
/goal $loopseed one-shotted Build the requested vertical slice and prove the complete user path works.
```

or:

```text
$loopseed one-shotted <one natural-language goal>
```

Use ordinary LoopSeed for small or tightly scoped tasks. One-Shotted mode is justified when repeated user prompting would otherwise be needed across planning, implementation, verification, and repair.

## Bootstrap

From the target project root:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py init \
  --root . \
  --goal "<the exact user-authorized goal>"
```

This creates:

```text
.loopseed/one-shotted/
├── project-identity.md
├── architecture-contract.md
├── goal-contract.json
├── acceptance.json
├── expert-registry.json
├── state.json
├── evidence.jsonl
├── defects.jsonl
└── final-report.json       # only after successful finalization
```

The directory is a small control plane, not a work diary. Keep current goal, gates, latest state, evidence events, and defect events. Never store secrets, private reasoning, or large copied sources.

## State machine

```text
BIND
  resolve authority, project identity, and observable outcome
    ↓
PLAN
  choose the smallest coherent route and ownership boundaries
    ↓
IMPLEMENT
  make the authorized change; keep integration central
    ↓
VERIFY
  independent verifier runs the real gate
    ├── PASS → next gate or FINALIZE
    └── FAIL → REPAIR
                 ↓
               IMPLEMENT / VERIFY
```

`transition --no-progress` counts stalled rounds. At two consecutive no-progress rounds, the control plane forces `PLAN` and requires root-cause diagnosis plus a materially different route.

## Acceptance gates

A gate is a decision, not an aspiration. It names:

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
  --id BUILD \
  --title "Production build" \
  --criterion "The documented production build command exits zero" \
  --owner lead \
  --verifier verifier
```

Choose gates close to the real product. Depending on the goal, these may include build, boot, complete user flow, screenshots at named states, data integrity, accessibility, performance distribution, regression, or artifact existence. Do not create dozens of low-value gates.

## Independent evidence

Only the declared verifier may record a gate verdict:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py record \
  --root . \
  --gate BUILD \
  --result PASS \
  --actor verifier \
  --summary "Production build completed successfully" \
  --command "npm run build"
```

The implementation owner may produce candidate evidence, but cannot approve its own gate. Agreement is not proof. Prefer commands, runtime inspection, fixed screenshots, diffs, artifacts, or complete scripted flows.

A `FAIL` automatically moves the run to `REPAIR`. The repair must be re-run by the verifier; changing the prose does not change the gate.

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

Resolve with another event using the same ID and `--status RESOLVED`. The latest event controls current defect status. Open P0 or P1 defects prevent finalization.

## Repair, rollback, and coupling

Use parallel work only for independent investigation, tests, or isolated candidates. Rendering, product composition, architecture, shared state, and other coupled concerns need one sequential owner. When a change breaks an already-passed gate, repair it or restore the last passing state before continuing.

Do not loop on the same diagnosis. After two no-progress rounds:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition --root . --no-progress
```

The run returns to `PLAN` and requires a different route.

## Completion

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py finalize --root .
```

Finalization fails closed unless:

- at least one required gate exists;
- every required gate is `PASS`;
- each PASS references evidence written by its declared verifier;
- no P0/P1 defect remains open;
- the contracts and ledgers are internally consistent.

Successful finalization writes `final-report.json`, moves phase to `FINALIZE`, and sets status to `VERIFIED`. Hooks stop continuing after a terminal state.

## Economy rules

- One instruction does not imply maximal fanout.
- Start with one lead and one evidence truth.
- Add a verifier only at actual gates; add specialists only for independent gaps.
- Keep outputs structured and bounded.
- Update state on decisions, evidence, route changes, blockers, and terminal results—not every tool call.
- Reuse the project’s existing build/test/runtime harness before building new orchestration.
- Prefer the closest real acceptance test over long status reports.
