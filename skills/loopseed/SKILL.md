---
name: loopseed
description: Run a plan-bound evidence loop from an explicit `$loopseed` goal. Use `$loopseed one-shotted <goal>` only when the user explicitly requests one-instruction autonomous completion with minimal human intervention, independent verification, repair, and fail-closed finalization.
---

# LoopSeed

Use only after an explicit `$loopseed` invocation. Never infer activation from similar wording or an old state file.

LoopSeed has two operating modes:

- **Standard:** `$loopseed <goal>` — the smallest useful Explore → Act → Observe → Verify → Adapt loop.
- **One-Shotted:** `$loopseed one-shotted <goal>` — one human authorization starts a durable, contract-bound run that autonomously plans, implements, verifies, repairs, and finalizes.

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
2. Run the bundled control plane from the target project root:

   ```bash
   python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py init --root . --goal "<goal>"
   ```

3. Inspect project authority before substantial implementation.
4. Add observable acceptance gates before claiming progress. Every gate must name an implementation owner and a different verifier.
5. Keep `.loopseed/one-shotted/` current at decision boundaries, not after every thought.
6. Follow the state machine:

   ```text
   BIND → PLAN → IMPLEMENT → VERIFY
                        FAIL ↓    ↓ PASS
                           REPAIR → VERIFY → FINALIZE
   ```

7. Use the CLI to append evidence and defects; do not hand-edit a PASS to bypass the judge.
8. Call `finalize` only after all required gates have independent PASS evidence and no open P0/P1 defect.

## One-Shotted invariants

- One lead owns integration. Parallel writers require isolation; coupled concerns stay sequential.
- Acceptance is declared before substantial implementation.
- A worker cannot approve its own gate.
- A failed gate moves the run to `REPAIR`; repair must be reverified.
- Keep only changes that preserve already-passed gates; otherwise repair or roll back.
- Two no-progress rounds force root-cause replanning and a materially different route.
- Only the finalizer may write `VERIFIED`.
- `BLOCKED` requires the exact missing permission, input, authority decision, or irreversible-risk gate plus the exact unblock condition.
- State and prose are control signals, never completion proof.
- Do not fan out agents ceremonially. Start with one lead and add a verifier or specialist only when the gate requires it.

## Terminal states

- `VERIFIED` — every required acceptance gate has direct, verifier-authored PASS evidence and no open P0/P1 defect.
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
