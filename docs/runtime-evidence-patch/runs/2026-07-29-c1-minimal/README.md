# C1 minimal preflight — 2026-07-29

## Verdict

`C1_RUNTIME_MISSING`

This run stopped at the mandatory zero-implementation preflight. No product task,
BLOCKED transition, negative evidence suite, or finalization was attempted.

## Binding

- Test ID: `2026-07-29-c1-minimal`
- LOOPSEED source branch: `experiment/evidence-governed-runtime-v0.5`
- Source commit: `9d77d0b3d4c32c3c5ab98df82977f3fc4e8af4da`
- Evidence branch: `experiment/c1-minimal-preflight-2026-07-29`
- Project stage: C1 runtime preflight
- Protected invariants: `main` unchanged; no PR; no manual state edit

## Direct evidence

1. `python skills/loopseed/scripts/one_shotted.py --help` exited 0 and listed
   only `init, add-gate, record, defect, transition, validate, finalize, status`.
2. `python skills/loopseed/scripts/one_shotted.py resume --help` exited 2 with
   `invalid choice: 'resume'`.
3. The public control-plane API in
   `skills/loopseed/scripts/one_shotted_core.py` exports no resume operation.
4. `record_gate_result` in
   `skills/loopseed/scripts/one_shotted_evidence.py` stores caller-supplied
   command and artifact strings and then writes the gate result. It does not
   execute the command or bind evidence to repository, candidate commit, and
   artifact hash.

The only repository-wide script/test match for the word `resume` was a hook
test using `source="resume"`; it is not a BLOCKED recovery command.

## Stop reason

The C1 protocol explicitly requires immediate stop when either an executable
resume path or a machine Evidence Runner is absent. Both are absent at the
bound source commit. Continuing with a real product task would only spend quota
to reconfirm a known runtime gap.

## Next narrow action

Implement, on a new runtime-development branch:

- a machine-enforced `resume` command for `BLOCKED -> ACTIVE/VERIFY`;
- fresh evidence validation against blocker ID, project binding, candidate
  commit, and artifact hash;
- a runner that executes the verification command and records exit status and
  bounded stdout/stderr;
- rejection tests for absent, stale, wrong-blocker, wrong-binding, drifted, and
  hand-forged evidence.

Then rerun only this single C1 test.
