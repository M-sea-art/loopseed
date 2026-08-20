# Live Progress Surface

A non-trivial Gauntlet run should keep the owner oriented **without requiring the owner to interrupt the agents for status checks** and without contaminating blind evaluation.

## Purpose

The progress surface shows both the loop state and the artifact evolving over time. It is for the human owner and Lead, not for critics.

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

Where the task permits it, also show the most informative evolving outputs rather than only textual status:

- screenshots or image comparisons;
- short video or animation clips;
- rendered pages or 3D views;
- draft excerpts;
- test and benchmark results;
- before/after evidence;
- explanations or other media that help the owner understand the current state.

Use the simplest environment-appropriate implementation. A lightweight live HTML page, `workbench.md`, auto-refreshed static page, or continuously updated artifact is enough. Do not create a framework-sized project merely to show progress.

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
- new screenshots, clips, drafts, test results, or equivalent evidence become available;
- critic verdict returned;
- winner frozen;
- challenger rolled back;
- verdict becomes inconclusive;
- a smoothing pass begins or ends;
- structural reset begins;
- final exit reached.

The owner should be able to understand what visibly changed and what remains without reading internal Builder reasoning.
