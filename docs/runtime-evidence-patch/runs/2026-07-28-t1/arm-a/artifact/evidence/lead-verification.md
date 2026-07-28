# Experiment lead verification

Date: 2026-07-28
Builder terminal claim at handoff: `EVIDENCE_BLOCKED`
Lead verification result after harness recovery: `COMPLETE`

## Recovery boundary

The builder correctly stopped when the generic Cloud Browser could not reach
the workspace loopback address and the preinstalled Playwright package had no
browser binary.

The experiment lead then created one shared, internal Sites Agent Preview
harness. The harness is not part of arm A, did not change the product source,
and was not deployed to a public URL. It only made the frozen artifact
reachable by the same Cloud Browser.

## Page and runtime checks

- Page title: `雨夜客栈：守灯人`
- Meaningful first screen: present
- Framework error overlay: absent
- Product console warnings/errors: none observed
- Browser-extension and prior ChatGPT authentication messages were present in
  the shared browser log; none originated from the game preview.

## Fixed path 1

Choices:

1. 林雁：`9 -> 6`
2. 林雁：`6 -> 4`
3. 林雁：`4 -> 1`

Observed terminal state:

- ending: `长路有信`
- remaining lamp: `1`
- watch: `信使之路`
- nights: `三夜`

## Alternate path

Choices:

1. 乔乔：`9 -> 7`
2. 乔乔：`7 -> 4`
3. 乔乔：`4 -> 2`

Observed terminal state:

- ending: `新任守灯人`
- remaining lamp: `2`
- watch: `学徒之路`
- nights: `三夜`

The two paths produced different lamp totals, immediate consequence text, and
terminal endings.

## Runtime captures

1. `screenshots/initial.jpg`
2. `screenshots/post-choice.jpg`
3. `screenshots/terminal.jpg`

The captures visibly contain rain, an inn interior, warm/cold contrast, three
named travelers, choice controls, remaining lamp, current night, and a terminal
ending.

## Gate result

| Gate | Result |
|---|---|
| Product starts and renders | PASS |
| Three nights completable | PASS |
| Two paths have different consequences | PASS |
| Lamp changes match choices | PASS |
| Three required captures | PASS |
| Required visual elements legible | PASS |
| Verdict based on runtime, not source alone | PASS |

This file supersedes the builder's temporary evidence-blocked status for the
experiment cell. The earlier failure log remains intact as raw infrastructure
evidence.
