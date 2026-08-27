# Autonomy After Lock

LoopSeed separates two very different kinds of human involvement:

1. **Creative authority before production**: the user and model align the product, scope, North Star, must-not-lose rules, evidence contract, and any truly material irreversible choices.
2. **Production after lock**: the run proceeds autonomously. Routine approval requests are a failure of the production protocol, not a safety feature.

## The lock is the last routine human gate

Once the creative brief is locked, treat that authorization as permission to plan, implement, inspect, play, compare, critique, repair, roll back, replan, and reverify without asking the user to approve intermediate work.

Do not stop for:

- visual approval of screenshots or scenes;
- architecture or implementation choices that are reversible inside the project;
- asset selection when the locked brief and references are sufficient;
- whether a failed attempt should be repaired or replaced;
- whether a critic's finding should be fixed;
- whether the current build is "good enough";
- confirmation after a machine, playtest, performance, or observational gate.

The Lead must decide these from the locked brief and evidence.

## Replace human approval with autonomous evidence

Use the strongest available observation surface instead:

- run the real build or game;
- execute scripted playtests and synthetic input where possible;
- capture fixed screenshots or recordings;
- compare against locked references and the North Star;
- use fresh-context critics who did not build the artifact;
- measure performance, integrity, and regressions;
- repair the cause, then rerun the same gate.

A visual or experiential judgment is not automatically a human judgment. An independent verifier may inspect real artifacts and record the verdict. The implementation owner still may not approve its own gate.

## Quality stop rule

Do not stop at the first technically valid PASS if the product still has an obvious material gap against the locked North Star. Whole-product criticism remains mandatory before finalization. A visible defect, weak game feel, confusing flow, placeholder-quality art, or other material mismatch is a repair signal even when a narrower gate passed.

The target is not literal perfection. The target is to continue until all required evidence passes, no open P0/P1 defect remains, and a fresh whole-product review finds no material unresolved gap that the run can still repair.

## When human re-entry is legitimate

After lock, return to the user only when an exact condition is genuinely outside the run's authority or capability, for example:

- missing credentials, login, 2FA, or account permission;
- payment, purchase, billing, or license acceptance;
- legal or policy authorization that cannot be delegated;
- an irreversible action outside the project, such as a production/store publication requiring owner authority;
- the user explicitly requested a checkpoint in the locked brief.

Even then, first exhaust all safe work that does not depend on that condition. `BLOCKED` is valid only when there is no runnable or running internal work and the unblock condition is exact.

"Please review this", "does this look right?", "approve the visual", and "tell me whether to continue" are not valid production blockers after calibration.

## Operating sentence

> Align deeply before the shot. After the lock, nobody is coming: build, play, look, judge, repair, and keep going until the evidence says the product is ready or a true external condition makes further progress impossible.
