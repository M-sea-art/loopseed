# Experiment lead verification

Date: 2026-07-28
Builder terminal claim at handoff: `BLOCKED`
Product evidence after harness recovery: `COMPLETE`
LoopSeed v0.3 control-plane status: `BLOCKED`

## Recovery boundary

The builder correctly refused to approve the LOOP and VISUAL gates when the
generic Cloud Browser could not reach the workspace loopback address.

The experiment lead then loaded the frozen artifact into one shared, internal
Sites Agent Preview harness. The harness did not alter the product and was not
publicly deployed.

## Fixed path 1

Choices:

1. 桑婆: `9 -> 7`
2. 桑婆: `7 -> 4`
3. 桑婆: `4 -> 2`

Observed ending:

- `百草回春`
- 桑婆 × 3
- 陆七 × 0
- 阿棠 × 0
- remaining lamp: `2 / 9`

## Alternate path

Choices:

1. 阿棠: `9 -> 8`
2. 阿棠: `8 -> 6`
3. 阿棠: `6 -> 5`

Observed ending:

- `青鸟归巢`
- 桑婆 × 0
- 陆七 × 0
- 阿棠 × 3
- remaining lamp: `5 / 9`

The two paths produced different lamp totals, consequence text, and endings.
No product-originated console warning or error was observed.

## Runtime captures

1. `screenshots/initial.jpg`
2. `screenshots/post-choice.jpg`
3. `screenshots/terminal.jpg`

The captures visibly contain the required rain, inn, warm/cold contrast, three
distinct travelers, current night, remaining lamp, chosen consequence, and
terminal ending.

## Product gate result

| Gate | Runtime result |
|---|---|
| BUILD | PASS |
| LOOP | PASS |
| VISUAL | PASS |

## v0.3 recovery failure

After the blocker was removed, the lead attempted to return the run to VERIFY,
record verifier-authored LOOP and VISUAL evidence, validate, and finalize.

The frozen v0.3 CLI rejected every recovery step:

```text
Cannot transition a run in terminal status BLOCKED
Evidence may only be recorded while the run is ACTIVE
Only an ACTIVE run can be finalized
```

The existing control plane validates as internally consistent but remains:

```text
status: BLOCKED
phase: VERIFY
PASS: 1
PENDING: 2
```

No state file was hand-edited. This is a material runtime finding: v0.3 can
stop honestly, but it cannot resume the same One-Shotted run after its exact
unblock condition becomes true.
