# LoopSeed Version Management

## Version Strategy

LoopSeed keeps the main branch as the stable protocol baseline. Experimental branches must represent one clear evolution path and must not silently replace earlier contracts.

## Current Version Map

| Version | Branch / State | Purpose | Status |
|---|---|---|---|
| v0.1 | initial source | Plugin foundation | archived baseline |
| v0.2 | main history | Project-agnostic autonomous loop, runtime escalation, state relay | completed |
| v0.3 | main history | One-Shotted mode, contract-bound planning, verification, repair, fail-closed finalization | current stable baseline |
| v0.4.x | design/protocol evolution | Improvement units, coupling awareness, Fresh Critic, merge discipline | protocol reference |
| v0.5 | experiment/evidence-governed-runtime-v0.5 | Binding, executable evidence, frontier state, stronger verdict model | experimental |

## Branch Rules

- `main`: stable release baseline only.
- `experiment/*`: isolated validation branches.
- Every experiment must document:
  - inherited baseline commit
  - changed contract
  - expected improvement
  - verification method
  - rollback condition

## v0.5 Scope

The v0.5 branch intentionally does not add more permanent agents.

Focus areas:

1. Project Binding Receipt
2. Executable Evidence Runner
3. Production Frontier State
4. Stronger completion verdicts

## Non-goals

- Do not convert LoopSeed into a large agent framework.
- Do not add roles without measurable control value.
- Do not replace evidence with self-reported summaries.
