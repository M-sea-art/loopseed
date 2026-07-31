---
name: loopseed
description: Run a plan-bound evidence loop from an explicit `$loopseed` goal. Use `$loopseed one-shotted <goal>` only when the user explicitly requests one-instruction autonomous completion with minimal human intervention, independent verification, repair, resumable blocking, and fail-closed finalization.
---

# LoopSeed

Use only after an explicit `$loopseed` invocation. Never infer activation from similar wording or an old state file.

LoopSeed has two operating modes:

- **Standard:** `$loopseed <goal>` — the smallest useful Explore → Act → Observe → Verify → Adapt loop.
- **One-Shotted:** `$loopseed one-shotted <goal>` — one human authorization starts a durable, contract-bound run that autonomously plans, implements, verifies, repairs, blocks honestly, resumes from fresh evidence, and finalizes.

“One-Shotted” means **one human instruction**, not one model response. Internal tool calls, tests, independent reviewers, repair rounds, and state recovery are expected. The mode reduces repeated prompting; it does not remove evidence or safety boundaries.

## Shared authority

Bind one root goal and acceptance to this order:

1. the user's explicit current instruction;
2. named project plans, milestones, product specifications, and reference files;
3. repository instructions such as `AGENTS.md`;
4. tests and the running product as evidence.

Existing implementation is evidence, not authority when it conflicts with the intended product.

## Standard mode

Use the cheapest loop that can close the goal:

1. **Explore** the closest real state and highest-value unknown.
2. **Act** with the smallest coherent authorized change.
3. **Observe** the running path, tests, UI, screenshots, artifacts, or source output.
4. **Verify** against the same acceptance conditions.
5. **Adapt** by repairing the cause or choosing a materially different route.

Default to one main thread, one writer, and one integration path. Delegate only independent work whose expected value exceeds coordination and token cost. Create `.loopseed.md` only when durable relay is actually needed. Read [playbook.md](references/playbook.md), [runtime-ladder.md](references/runtime-ladder.md), and [state-contract.md](references/state-contract.md) only when relevant.

## One-Shotted activation

For `$loopseed one-shotted <goal>`:

1. Read [one-shotted-mode.md](references/one-shotted-mode.md).
2. Initialize the bundled control plane from the target project root:

   ```bash
   python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py init --root . --goal "<goal>"
   ```

3. Inspect project authority before substantial implementation.
4. When a gate requires machine evidence, bind one immutable verification subject before running it:

   ```bash
   python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py bind \
     --root . --project <PROJECT_ID> --candidate <COMMIT> --artifact <PATH>
   ```

   In a real Git worktree, the actual `HEAD` must equal the bound candidate. The same binding is idempotent; a different subject requires a fresh run.
5. Add observable acceptance gates before claiming progress. Every gate must name an implementation owner and a different verifier. Add `--machine` when command execution and artifact identity are required.
6. Keep `.loopseed/one-shotted/` current at decision boundaries, not after every thought.
7. Follow the state machine:

   ```text
   BIND → PLAN → IMPLEMENT → VERIFY
                        FAIL ↓    ↓ PASS
                           REPAIR → VERIFY → FINALIZE
   ```

8. Use `run-evidence` for machine gates. PASS requires command exit `0`, correct actual Git identity when available, and one stable artifact hash before and after execution.
9. Use the CLI to append manual evidence and defects; do not hand-edit a PASS to bypass the judge.
10. Call `finalize` only after all required gates have valid independent evidence and no open P0/P1 defect.

## One-Shotted invariants

- One lead owns integration. Parallel writers require isolation; coupled concerns stay sequential.
- Acceptance is declared before substantial implementation.
- A worker cannot approve its own gate.
- A failed gate moves the run to `REPAIR`; repair must be reverified.
- Machine evidence is an integrity transaction: expected artifact = before artifact = after artifact.
- A verifier command that changes the bound artifact produces FAIL even when its exit code is zero.
- Keep only changes that preserve already-passed gates; otherwise repair or roll back.
- Two no-progress rounds force root-cause replanning and a materially different route.
- Only the finalizer may write `VERIFIED`.
- `BLOCKED` requires the exact missing permission, input, authority decision, or irreversible-risk gate plus the exact unblock condition.
- `BLOCKED` may resume only through fresh machine evidence for the active blocker; never edit state manually.
- State and prose are control signals, never completion proof.
- Do not fan out agents ceremonially. Start with one lead and add a verifier or specialist only when the gate requires it.

## Blocking and recovery

Failure, low quality, a failing test, uncertainty, or an exhausted first route are not blockers. They trigger repair, rollback, or replanning.

A true blocker may enter `BLOCKED`. Once the exact condition becomes true:

1. run `run-evidence --blocker <ID>` against the same project, candidate, and artifact;
2. require a fresh, integrity-stable machine PASS;
3. run `resume --evidence <ID> --actor <VERIFIER>`;
4. continue from `ACTIVE / VERIFY` and produce fresh gate evidence.

`VERIFIED` and `ABORTED` are irreversible terminal outcomes. `BLOCKED` allows the session to stop but remains recoverable through this explicit path.

## Reporting

At the end, report only:

- terminal verdict;
- direct evidence and final report path;
- bound project/candidate/artifact identity without secrets;
- changed scope;
- remaining non-blocking risk;
- exact unblock condition when blocked.

An ordinary LoopSeed invocation does not authorize changing LoopSeed itself.
