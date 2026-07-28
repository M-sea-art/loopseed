# One-Shotted Architecture Contract

1. **One integration owner.** Parallel writers require isolation; coupled work remains sequential.
2. **Predeclare acceptance.** Create observable gates before substantial implementation.
3. **Separate builder and judge.** A gate owner cannot be its verifier.
4. **Evidence over prose.** Commands, running UI, screenshots, artifacts, and deterministic checks decide status.
5. **Fail closed.** A failed gate enters `REPAIR`; it never becomes an informal pass.
6. **Repair or rollback.** Keep only changes that improve the goal without breaking passed gates.
7. **Reroute after stalling.** Two no-progress rounds force root-cause diagnosis and a materially different plan.
8. **Terminal truth.** Only the finalizer may write `VERIFIED`, and only after every required gate passes with verifier-authored evidence and no open P0/P1 defect.
9. **Honest blocking.** `BLOCKED` requires an exact missing permission/input/authority decision plus an exact unblock condition.
10. **Bounded records.** State stores the current decision surface; JSONL ledgers store compact evidence and defect events, not chain of thought.
