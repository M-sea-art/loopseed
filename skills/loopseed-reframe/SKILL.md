---
name: loopseed-reframe
description: "Discover the expert vocabulary and neighboring disciplines behind an unclear idea, verify sources, and rewrite the description. Use for $loopseed-reframe."
disable-model-invocation: true
---

Teach the operator the expert words for what they are building. Start from their own files, code and description, not a summary.

If their description could name more than one problem, first list the two or three problems it could be, each with the one term that names it and the sign that would tell it apart from the others. Then teach the words for the most likely one and say why you picked it.

1. Give 8 to 12 terms, ranked by how much each would change what gets built. For each, give the word and its meaning in one plain sentence, the part of their description it names, one real project, paper or system that uses it that way, with a link, and what it lets them ask an agent for.
2. Pick 2 or 3 neighboring fields that solved the same shape of problem under other names. For each, say what carries over, where the analogy breaks, and which terms come back.
3. Name what they didn't mention but should care about.
4. Rewrite their description with the new words.

Open every link and confirm it uses the term that way. Cut any citation you can't confirm. No padding.

## LoopSeed integration

In standalone use, return the vocabulary, analogies, overlooked considerations, and rewritten description in the user's language; do not implement it. Preserve the user's original goal, identity-critical constraints, and authority. Label uncertain interpretations as hypotheses. If source access is unavailable, say so; omit unverifiable citations, never manufacture examples, and give fewer terms rather than padding. When LoopSeed reads this method during an authorized run, it may use only the investigation that resolves the current question and carry the resulting insight into the work. It need not produce the standalone report unless the user requests it. Do not expand a bounded request into a continuing vision.

Derived from [pstack](https://github.com/cursor/plugins/tree/main/pstack), by Lauren Tan. See [MIT notice](../../licenses/pstack-MIT.txt).
