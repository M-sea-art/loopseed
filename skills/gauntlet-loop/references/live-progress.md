# Live Progress Surface

A non-trivial Gauntlet run should keep the owner oriented without contaminating blind evaluation.

## Purpose

The progress surface shows the work evolving over time. It is for the human owner and Lead, not for critics.

Useful fields:

```text
GOAL
BAR
CURRENT INCUMBENT
CURRENT QUALITY SURFACE
SINGLE BIGGEST GAP
CURRENT ROUND
ROUND HISTORY
FREEZE / ROLLBACK / INCONCLUSIVE EVENTS
EVIDENCE LINKS
CURRENT STATUS
```

Use the simplest environment-appropriate implementation. A lightweight live page, auto-refreshed static page, or continuously updated page artifact is enough. Do not create a framework-sized project merely to show progress.

## Anti-leak boundary

The progress surface may contain information that invalidates blind review, including:

- which candidate is newer;
- what the Builder intended to fix;
- prior verdicts;
- current expected winner;
- round order;
- failed experiments.

Therefore:

- never pass the progress page to a blind critic;
- never use it as critic evidence;
- never let candidate labels on the page match blind candidate labels;
- build critic packets from the evidence source directly, not by copying from the progress page.

The progress page is a **control surface**, not a quality gate.

## Update cadence

Update after meaningful state changes rather than every tool call:

- bar selected or strengthened;
- candidate produced;
- critic verdict returned;
- winner frozen;
- challenger rolled back;
- verdict becomes inconclusive;
- structural reset begins;
- final exit reached.

The owner should be able to understand what changed and what remains without reading internal Builder reasoning.
