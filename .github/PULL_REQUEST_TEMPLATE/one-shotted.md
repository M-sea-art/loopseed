## One-Shotted change

### Authorized goal

<!-- One observable outcome. -->

### Acceptance gates

- [ ] Required gates are declared before completion.
- [ ] Each gate has a different owner and verifier.
- [ ] Machine commands ran through `run-evidence`; human/visual evidence artifacts are hashed.
- [ ] Candidate and verifier source are committed; non-ignored untracked content is bound evidence/artifact content.

### Failure behavior

- [ ] Failed gates enter repair or are rolled back.
- [ ] Open P0/P1 defects are resolved or explicitly block the run.
- [ ] No-progress rounds trigger root-cause replanning rather than repetition.
- [ ] Every required task is `SUCCEEDED`; disposable optional arms are explicitly `CANCELLED`.

### Validation

<!-- Build, tests, runtime flow, screenshots, artifacts, or other direct evidence. -->

### Terminal verdict

<!-- VERIFIED / BLOCKED / ABORTED; do not use a progress label as proof. -->

- [ ] `final-report.json` cross-validates against the current run, evidence, tasks, and verification binding.
