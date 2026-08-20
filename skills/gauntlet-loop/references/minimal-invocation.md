# Minimal Gauntlet Invocation

The user-facing prompt should stay short. The skill carries the protocol.

## Run it in a real agentic harness

The generated launcher is intended for an environment such as Claude Code, Codex, or another agentic harness that can touch the artifact: read and edit files, run tools and code, render or inspect output, and create independent subagents or contexts when available.

A plain chat may generate or critique the launcher, but must not pretend it executed the full loop when it cannot inspect and change the real artifact.

## Input shape

A minimal invocation is enough:

```text
Run a Gauntlet Loop for: <GOAL>
References: <OPTIONAL REFERENCES>
```

The Lead should resolve the strongest concrete bar itself when references are missing.

## Bar rule

Choose the strongest bar an evaluator can actually inspect, execute, compare, or measure. Prefer real targets, frozen incumbents, executable tests, real benchmarks, or a clearly falsifiable evaluation protocol over adjectives.

Explain the chosen bar in one sentence when the user asked for a prompt or planning output.

A useful bar may intentionally be harder than the current run can realistically reach. Its job is to provide direction and prevent premature `good enough` stopping. Do not lower it merely to create a PASS.

## Prompt compiler

When the user wants a short prompt for Claude Code, Codex, or another agent, compile the goal and bar into a launcher like this:

```text
I want you to achieve: <GOAL>

Quality bar: <BAR>. Compare the real output directly against it.

Choose the approach yourself. Divide the goal into the smallest pieces that can be improved and judged independently. For each important independent piece, use a builder and a separate fresh-context critic when the environment supports it. Each critic must inspect the real output, compare it directly with the bar, identify the single biggest remaining gap, and send that gap back for another round. Use blind A/B comparison when it is meaningful. Keep only proven wins, roll back regressions, and keep looping without an arbitrary round cap until the output meets or beats the bar, improvements become too small to matter, the available compute is no longer worth spending, a structural reset is required, or I stop the run.

Maintain a simple live progress page showing the work evolving over time with the most useful screenshots, videos, drafts, test results, or other media, but never expose it or Builder reasoning to blind critics. After major parallel waves, use a fresh whole-artifact smoothing pass when independently improved pieces need coherence. Use subagents and ultracode when available and useful.
```

## Keep it minimal

Do not paste the entire Gauntlet protocol into the launcher unless the execution environment cannot load the skill.

Do not prescribe:

- architecture;
- exact decomposition;
- fixed number of builders;
- fixed number of rounds;
- implementation stack unless the user already chose one.

The Lead owns the approach. The protocol owns the evidence discipline.

## Important interpretation

`Keep looping until our output wins or I stop` is motivational shorthand, not permission for infinite local patching or bar-lowering.

Valid exits remain:

```text
PASS / WIN
owner says it is ready
improvements become too small to matter
compute is no longer worth spending
ROLLBACK
INCONCLUSIVE
STRUCTURAL_RESET
BLOCKED by an exact external condition
owner stops
```

The bar may become stricter when stronger evidence appears. It must never be silently weakened to manufacture a win.
