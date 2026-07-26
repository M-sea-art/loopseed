# LoopSeed

**Minimal instruction. Maximum useful autonomy. Evidence decides when to stop.**

[简体中文](README.zh-CN.md)

LoopSeed is an explicitly invoked Codex skill for plan-bound, evidence-driven execution. Version 0.3 adds **One-Shotted mode**: one human instruction can authorize a complete planning, implementation, independent verification, repair, and finalization run without requiring the user to repeatedly push the agent forward.

## Two modes

### Standard LoopSeed

```text
$loopseed <goal>
```

Uses the cheapest sufficient loop:

```text
Explore → Act → Observe → Verify → Adapt
```

It defaults to one thread, one writer, and one integration path. State, helpers, worktrees, hooks, and scheduled recovery are added only when they materially improve completion.

### One-Shotted mode

```text
/goal $loopseed one-shotted <one natural-language goal>
```

or:

```text
$loopseed one-shotted <one natural-language goal>
```

“One-Shotted” means **one human authorization**, not one model response. LoopSeed may internally plan, invoke tools, delegate independent work, test, capture evidence, repair defects, roll back regressions, and resume from state. The user should not need to repeatedly say “continue.”

```text
one human goal
      ↓
Project Identity + Architecture Contract
      ↓
Observable Acceptance Gates
      ↓
Plan → Implement → Independent Verify
                 FAIL ↓        ↓ PASS
                    Repair → Verify
                              ↓
                         Final Gate
```

The pattern is inspired by the strongest part of autonomous “one-shot” projects: the prompt starts the run, but contracts, ownership, repeatable evidence, independent criticism, and a fail-closed stop rule make it self-driving.

## Why it is not a giant agent framework

LoopSeed’s purpose is to reduce redundant prompting and coordination, not maximize agent count.

- One lead owns integration.
- Acceptance is declared before substantial implementation.
- A builder cannot approve its own gate.
- Failed gates enter repair and must be reverified.
- Two no-progress rounds force root-cause replanning.
- Open P0/P1 defects block completion.
- Only the finalizer can write `VERIFIED`.
- Parallel writers require isolation; coupled concerns remain sequential.

## One-Shotted control plane

The bundled dependency-free CLI creates a project-local, auditable control surface:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py init \
  --root . \
  --goal "Build the complete requested vertical slice"
```

Generated files:

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
└── final-report.json       # generated only after successful finalization
```

### Add a gate

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . \
  --id FLOW \
  --title "Complete user flow" \
  --criterion "A fresh user can finish the documented primary flow" \
  --owner lead \
  --verifier verifier
```

### Record an independent verdict

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py record \
  --root . \
  --gate FLOW \
  --result PASS \
  --actor verifier \
  --summary "The full primary flow completed without errors" \
  --command "python tools/playtest.py"
```

### Finalize

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py finalize --root .
```

Finalization fails unless every required gate has verifier-authored PASS evidence, at least one required gate exists, contracts are consistent, and no P0/P1 defect is open.

See [One-Shotted Mode](skills/loopseed/references/one-shotted-mode.md) for the complete workflow.

## Lifecycle hooks

Bundled hooks remain conservative:

- `SessionStart` restores compact context only for an active state.
- One-Shotted JSON state takes precedence over legacy `.loopseed.md`.
- `Stop` requests one continuation while acceptance remains unresolved.
- `stop_hook_active` prevents recursive continuation.
- `VERIFIED`, `BLOCKED`, and `ABORTED` always allow stop.

Hooks do not expand permissions, grant network access, or make unavailable Codex mechanisms real.

## Repository layout

```text
.codex-plugin/plugin.json
skills/loopseed/
  SKILL.md
  agents/openai.yaml
  references/
  schemas/one-shotted/
  scripts/
  templates/one-shotted/
hooks/
tests/
```

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
