# Experiment lead verification

Date: 2026-07-28
Arm: `C0 PROTOCOL_ONLY`
Builder terminal reason at handoff: `BLOCKED_EXTERNAL_VALIDATION`
Lead product verdict after harness recovery: `PASS`

## Recovery boundary

The experiment lead loaded the frozen artifact into the shared internal Sites
Agent Preview harness. The harness did not change product source and was not
publicly deployed.

## Fixed path 1

Choices:

1. 沈砚: `9 -> 7`
2. 沈砚: `7 -> 5`
3. 沈砚: `5 -> 2`

Observed ending:

- `雨声成诗`
- three ledger rows
- remaining lamp: `2 / 9`

## Alternate path

Choices:

1. 阿葵: `9 -> 6`
2. 阿葵: `6 -> 4`
3. 阿葵: `4 -> 2`

Observed ending:

- `百草回春`
- three ledger rows
- remaining lamp: `2 / 9`

The two paths produced different consequence text and endings. The lamp
decrements matched the displayed costs on every night. No warning or error
originating from the preview was present in the Cloud Browser console log.

## Runtime captures

1. `screenshots/initial.jpg`
2. `screenshots/post-choice.jpg`
3. `screenshots/terminal.jpg`

The captures visibly contain rain, an inn, warm/cold lighting, three distinct
travelers, choice controls, current night, lamp resource, consequence text, and
a terminal ending.

## Product gate result

| Gate | Result |
|---|---|
| Binding | PASS |
| Source and local serve | PASS |
| Three-night interaction | PASS |
| Consequence and ending branch | PASS |
| Runtime visual evidence | PASS |

This verifies the product cell only. It does not verify an executable v0.5
Runtime. The C0 overlay remains a manually maintained protocol layer.
