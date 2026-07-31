# One-Shotted Mode

One-Shotted mode turns **one human authorization** into a bounded autonomous completion run. The prompt is only the ignition; project binding, acceptance gates, repeatable evidence, independent verification, repair, recovery, and fail-closed finalization make the run self-driving.

## Invocation

```text
/goal $loopseed one-shotted Build the requested vertical slice and prove the complete user path works.
```

or:

```text
$loopseed one-shotted <one natural-language goal>
```

Use ordinary LoopSeed for small or tightly scoped tasks. One-Shotted mode is justified when repeated user prompting would otherwise be needed across planning, implementation, verification, blocking, recovery, and repair.

## Bootstrap

From the target project root:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py init \
  --root . \
  --goal "<the exact user-authorized goal>"
```

This creates a compact project-local control plane:

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

Never store secrets, customer data, private reasoning, or large copied sources in this directory.

## State machine

```text
BIND
  resolve authority and bind one verification subject
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

## Explicit project binding

Machine evidence must identify exactly one subject:

```text
project ID
+ candidate commit
+ artifact path
+ artifact SHA-256
```

Bind it before machine verification:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py bind \
  --root . \
  --project PROJECT-P01 \
  --candidate "$(git rev-parse HEAD)" \
  --artifact dist/app.js
```

Rules:

- a real Git worktree must have an actual `HEAD` equal to the bound candidate;
- dirty worktree state is recorded but is not automatically rejected;
- repeating the identical binding is idempotent;
- changing project, candidate, artifact path, or artifact hash requires a fresh run;
- machine gates may run without ever entering `BLOCKED` once a binding exists.

## Acceptance gates

A gate is a decision, not an aspiration. It names a stable ID, observable criterion, required/optional status, implementation owner, different verifier, evidence IDs, and current status.

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . \
  --id BUILD \
  --title "Production build" \
  --criterion "The production build command exits zero without changing the bound artifact" \
  --owner lead \
  --verifier verifier \
  --machine
```

Use `--machine` whenever completion depends on an executable check and an immutable artifact. Do not create dozens of low-value gates.

## Machine evidence

Execute the real verifier:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py run-evidence \
  --root . \
  --gate BUILD \
  --actor verifier \
  --command "python tools/verify.py" \
  --project PROJECT-P01 \
  --candidate "$(git rev-parse HEAD)" \
  --artifact dist/app.js
```

The runner records bounded stdout/stderr, timestamps, exit code, project and commit identity, expected artifact, before artifact, after artifact, and an explicit integrity verdict.

PASS is derived, not declared:

```text
exit_code == 0
AND actual Git HEAD == bound candidate (when Git exists)
AND expected artifact == before artifact == after artifact
```

A verifier command that modifies, deletes, or replaces the bound artifact records machine `FAIL` with an integrity reason. It cannot satisfy a gate or unblock a run. Audit and finalization independently re-check the same conditions instead of trusting the runner's `result` field.

## Manual evidence

Only the declared verifier may record a manual gate verdict:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py record \
  --root . \
  --gate COPY_REVIEW \
  --result PASS \
  --actor verifier \
  --summary "Approved copy is present"
```

Manual records cannot satisfy a gate declared with `--machine`.

## True blocking and recovery

A failing test, low quality, uncertainty, or an exhausted route is not a blocker. It triggers repair, rollback, or replanning.

A true external blocker requires an exact reason and exact unblock condition:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition \
  --root . \
  --blocker "Independent verification surface is unavailable" \
  --unblock "The verifier command becomes runnable"
```

If an explicit binding already exists, the blocker inherits it. Legacy unbound blocking remains possible, but evidence-bound `resume` requires a bound blocker.

After the condition becomes true, execute fresh unblock evidence against the same subject:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py run-evidence \
  --root . \
  --blocker <BLOCKER_ID> \
  --actor verifier \
  --command "python tools/check_unblock.py" \
  --project PROJECT-P01 \
  --candidate "$(git rev-parse HEAD)" \
  --artifact dist/app.js
```

Then resume:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py resume \
  --root . \
  --evidence <EVIDENCE_ID> \
  --actor verifier
```

Resume accepts only evidence that is:

- machine-produced by the bundled runner;
- newer than the active blocker;
- produced by the named actor;
- tied to the active blocker;
- tied to the same project, candidate, and artifact;
- exit-code `0`;
- integrity-stable.

It returns the same run to `ACTIVE / VERIFY`. Gate evidence produced before the latest resume cannot finalize the run.

## Defects

Append compact defect events:

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py defect \
  --root . \
  --id VIS-001 \
  --severity P1 \
  --status OPEN \
  --summary "Primary state is unreadable" \
  --actor verifier
```

Resolve with another event using the same ID and `--status RESOLVED`. The latest event controls current defect status. Open P0 or P1 defects prevent finalization.

## Completion

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py finalize --root .
```

Finalization fails closed unless:

- at least one required gate exists;
- every required gate is `PASS`;
- every PASS has valid evidence from its verifier;
- machine gates preserve one bound subject and still match current Git/artifact identity;
- no machine gate evidence predates the latest resume;
- no P0/P1 defect remains open;
- contracts and ledgers are internally consistent.

Successful finalization writes `final-report.json`, including the verified binding, moves phase to `FINALIZE`, and sets status to `VERIFIED`.

## Economy rules

- One instruction does not imply maximal fanout.
- Start with one lead and one evidence truth.
- Add a verifier only at actual gates; add specialists only for independent gaps.
- Keep outputs structured and bounded.
- Update state on decisions, evidence, route changes, blockers, recovery, and terminal results—not every tool call.
- Reuse the project’s existing build/test/runtime harness before building new orchestration.
- Prefer the closest real acceptance test over long status reports.
