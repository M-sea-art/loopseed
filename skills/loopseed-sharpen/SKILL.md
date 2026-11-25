---
name: loopseed-sharpen
description: "Deepen a task through expert methods, original evidence, experiments, and independent checks without enlarging scope. Use for $loopseed-sharpen."
disable-model-invocation: true
---

I want a deeper version of this task, not a bigger one. Before rewriting it, do four things:

1. Say what a top professional in this field would do here that I'm not asking for.
2. Name the rawest material they would start from instead of what has already been digested for me.
3. Name the specific methods and tools they would use.
4. Say what, other than you or me, would show the result is right.

Then rewrite my prompt to ask for exactly that.

Have the rewritten prompt ask the agent to prototype any choice an experiment can settle and recommend an option based on what it observed. Leave product or preference choices that no experiment can settle for me to make.

## LoopSeed integration

In standalone use, return the rewritten prompt and the four findings in the user's language; do not execute the task. Preserve the user's constraints, permissions, budget, and intended scope. Distinguish a feasible experiment from a proposed one; do not claim any experiment ran. When LoopSeed reads this method during an authorized run, it may apply only the useful parts and perform affordable, reversible experiments within the original authorization. An open vision can delegate design judgment; do not assume a bounded task delegates unrelated product decisions. Leave choices outside the delegated authority to the user. A suggested check is not acceptance evidence, and this method cannot change a bound One-Shotted contract.

Derived from [pstack](https://github.com/cursor/plugins/tree/main/pstack), by Lauren Tan. See [MIT notice](../../licenses/pstack-MIT.txt).
