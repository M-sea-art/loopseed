# LoopSeed

[简体中文](README.zh-CN.md)

Give Codex a vision for the experience you want. LoopSeed v0.9.0 lets the agent discover what to improve, change the product and reconsider its own ideas in light of what actually happens.

```text
$loopseed Give players a reason to start another voyage after their first trip to port.
```

> Within the authority you have been given, take responsibility for this project. Discover and realize the experience most worth pursuing. Let the work itself and the people who use it change your mind about any design judgment, including yours and the user's, and decide where to go next.

## Choosing an invocation

| What you want | Example | When work ends |
|---|---|---|
| A continuing project vision | `$loopseed Make the first round worth playing again.` | The agent chooses subsequent improvements within the authorization. An owner stop, exhausted allowance or genuine external blocker ends the run. |
| A bounded change | `$loopseed Fix the hand disappearing after a saved game is loaded.` | The agent delivers after checking that the hand survives a real save and reload. |
| Formal acceptance of a deliverable | `$loopseed one-shotted Deliver a playable slice with verified save, reload and restart.` | The strict runtime issues a receipt for the bound candidate after its required hard floors and quality bars pass independent verification. |

## Continuing in Codex

A running Codex Goal can carry a vision across turns. On a surface with the Goal command, start it directly with `/goal $loopseed <vision>`. When a session needs a handoff, the agent keeps the vision, latest observed change and open question in the project's `.loopseed.md`. Reopening the project provides that context for a fresh look at the actual work. A stop request or exhausted allowance takes priority. [State and recovery](skills/loopseed/references/state-contract.md#vision)

## Quality and delivery

When an actual question calls for a reference, a fresh critic or a blind comparison, the agent can use that method. Choosing One-Shotted explicitly brings in its full delivery protocol, including first-hand evidence for the running product, commit and artifact binding, recovery, and independent verification. Existing active One-Shotted runs follow their recorded protocol. [Quality methods](skills/loopseed/references/quality-methods.md) · [One-Shotted guide](skills/loopseed/references/one-shotted-mode.md)

## Validate locally

```bash
python -m json.tool .codex-plugin/plugin.json >/dev/null
find skills/loopseed/schemas skills/loopseed/templates -name '*.json' -print0 \
  | xargs -0 -n1 python -m json.tool >/dev/null
python tools/verify_usage_guide_version.py
python -m compileall -q hooks skills/loopseed/scripts tests tools
python -m unittest discover -s tests -v
```

## More detail

- [Side-by-side game trial and playable builds](docs/reviews/v0.9.0-playtest/README.md)
- [Production usage guide — 中文](docs/usage-guide.zh-CN.md)
- [One-Shotted mode](skills/loopseed/references/one-shotted-mode.md)
- [Autonomy after lock](skills/loopseed/references/autonomy-after-lock.md)
- [State contracts](skills/loopseed/references/state-contract.md)
- [Runtime ladder](skills/loopseed/references/runtime-ladder.md)
- [Acknowledgements](ACKNOWLEDGEMENTS.md)

## License

MIT. See [LICENSE](LICENSE).
