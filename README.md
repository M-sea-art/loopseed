# LoopSeed

**Minimal instruction. Maximum useful autonomy. Evidence decides when to stop.**

[简体中文](README.zh-CN.md)

LoopSeed is an explicitly invoked Codex skill for plan-bound, evidence-driven execution. The released `main` baseline is 0.3.0. The C1.1 experimental prerelease adds explicit project binding, machine-executed evidence, resumable `BLOCKED` runs, and integrity-stable finalization.

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

“One-Shotted” means **one human authorization**, not one model response. LoopSeed may internally plan, invoke tools, delegate independent work, test, capture evidence, repair defects, roll back regressions, block honestly, and resume from fresh evidence. The user should not need to repeatedly say “continue.”

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

### Bind one verification subject

Before a machine gate, bind the run to one project, candidate commit, and artifact:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py bind \
  --root . \
  --project PROJECT-P01 \
  --candidate "$(git rev-parse HEAD)" \
  --artifact dist/app.js
```

In a real Git worktree, the CLI independently verifies the actual `HEAD`. Repeating the same binding is idempotent; changing the project, candidate, or artifact requires a fresh run.

### Add a gate

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . \
  --id FLOW \
  --title "Complete user flow" \
  --criterion "A fresh user can finish the documented primary flow" \
  --owner lead \
  --verifier verifier \
  --machine
```

`--machine` prevents a prose-only `record PASS` from satisfying the gate.

### Execute machine evidence

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py run-evidence \
  --root . \
  --gate FLOW \
  --actor verifier \
  --command "python tools/playtest.py" \
  --project PROJECT-P01 \
  --candidate "$(git rev-parse HEAD)" \
  --artifact dist/app.js
```

Machine PASS requires all of the following:

```text
command exit code == 0
actual Git HEAD == bound candidate (when Git is present)
bound artifact hash == before-command hash == after-command hash
```

If the verifier command changes or deletes the bound artifact, evidence is recorded as `FAIL` and cannot satisfy a gate or unblock a run.

### Block and resume

A true external blocker may stop safely:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition \
  --root . \
  --blocker "Independent verification surface is unavailable" \
  --unblock "The verifier command becomes runnable"
```

After the condition becomes true, produce fresh unblock evidence against the same binding:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py run-evidence \
  --root . \
  --blocker <BLOCKER_ID> \
  --actor verifier \
  --command "python tools/check_unblock.py" \
  --project PROJECT-P01 \
  --candidate "$(git rev-parse HEAD)" \
  --artifact dist/app.js

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py resume \
  --root . \
  --evidence <EVIDENCE_ID> \
  --actor verifier
```

`resume` accepts only fresh, machine-produced, integrity-stable evidence for the active blocker and returns the same run to `ACTIVE / VERIFY`.

### Manual independent verdicts

Non-machine gates may still use compact verifier-authored records:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py record \
  --root . \
  --gate COPY_REVIEW \
  --result PASS \
  --actor verifier \
  --summary "The approved copy is present"
```

### Finalize

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py finalize --root .
```

Finalization fails unless every required gate has valid verifier evidence, machine gates retain one bound subject, contracts are consistent, the current artifact and Git identity still match, and no P0/P1 defect is open.

See [One-Shotted Mode](skills/loopseed/references/one-shotted-mode.md) for the complete workflow.

## Lifecycle hooks

Bundled hooks remain conservative:

- `SessionStart` restores compact context only for an active state.
- One-Shotted JSON state takes precedence over legacy `.loopseed.md`.
- `Stop` requests one continuation while acceptance remains unresolved.
- `stop_hook_active` prevents recursive continuation.
- `VERIFIED`, `BLOCKED`, and `ABORTED` allow the current session to stop.
- `BLOCKED` is recoverable only through the explicit evidence-bound `resume` command.

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
