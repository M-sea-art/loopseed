# LOOPSEED C1.2 — Pallet Town external evidence run

Date: 2026-07-31

## Purpose

This is a deliberately small, low-cost external-case evaluation. It tests whether a strong one-message game project can be converted from an attractive repository claim into repeatable evidence.

Subject repository: `PauliusOS/pallet-town-3d`

Frozen subject commit: `d49e0c0de836892133b3b21f50c9d29749879db5`

The subject repository is read-only. This experiment changes only the LOOPSEED experiment branch.

## Fixed scope

Run exactly these engineering gates:

1. dependency installation with `npm ci`
2. `npm run check`
3. `npm test`
4. `npm run build`

Run exactly these three fixed visual shots from the subject's own shot contract:

- `town_reveal`
- `lab_door`
- `starters_out`

Record:

- command exit codes and elapsed time
- subject commit and runner environment
- page-ready time and the subject's per-step `World.buildTimings`
- screenshot files
- FPS, draw calls, triangles, textures, geometries, and shader programs reported by the subject capture harness
- browser console errors
- capture backend and any fallback reason
- final `PASS`, `PARTIAL`, `FAIL`, or `BLOCKED` state

## Capture modes

The first attempt runs the subject's unmodified `tools/capture.mjs`. That script requests the Metal ANGLE backend.

GitHub-hosted Linux runners may not support that backend. When the exact attempt fails for environmental reasons, the experiment creates a temporary copy of the capture script, changes only the ANGLE backend from `metal` to `swiftshader`, and retries.

The fallback is useful for deterministic visual inspection, but its FPS is **not** comparable to native GPU performance. A fallback-only result must therefore be `PARTIAL`, never full `PASS`.

## Verdict rules

- `PASS`: install, check, test, build, and the unmodified three-shot capture all pass.
- `PARTIAL`: engineering gates pass and all three screenshots are produced only through the declared SwiftShader fallback.
- `FAIL`: any engineering gate fails, or the application boots but a required shot cannot be produced because of a project defect.
- `BLOCKED`: the runner, browser, package registry, permissions, or another external condition prevents reaching a valid project verdict.

No repository description, prompt claim, code comment, or self-authored `AAA` label can substitute for the above evidence.

## Stop conditions

The run stops after:

- one unmodified capture attempt; and
- at most one declared SwiftShader fallback attempt.

It does not enter an open-ended repair loop and does not modify the subject repository.

## Outputs

The workflow uploads a single artifact named `c1-2-pallet-town-evidence` containing:

```text
evidence/
├── command-results.json
├── environment.txt
├── install.log
├── check.log
├── test.log
├── build.log
├── preview.log
├── capture-exact.log
├── capture-fallback.log        # only when needed
├── probe.json
├── summary.json
├── summary.md
└── shots/
    ├── town_reveal.png
    ├── lab_door.png
    ├── starters_out.png
    └── manifest.json
```

A human or independent critic must inspect the three PNGs before any visual-quality conclusion is recorded in the repository.