# LoopSeed

[English](README.md)

给 Codex 一句你希望玩家获得的体验。LoopSeed v0.9.0 让模型自己发现什么值得改，动手改变作品，再用实际表现和使用者反馈修正判断。

```text
$loopseed 让玩家打完第一局，就想再开一局。
```

> 在授权范围内，把这个作品当作你负责的项目，主动发现并实现最值得追求的体验，让作品的实际表现和使用者的反馈帮助你重新审视任何既有判断，包括我和你自己的判断，并决定下一步往哪里走。

## 三种委托

| 你的意图 | 调用示例 | 什么时候交付 |
|---|---|---|
| 给项目一个长期愿景 | `$loopseed 让玩家打完第一局，就想再开一局。` | 模型在授权内继续寻找值得做的事。用户叫停、额度耗尽或出现确切外部阻塞时，保存进度并说明原因。 |
| 完成一个具体任务 | `$loopseed 修好读档后丢失手牌。` | 实际存档、读档，确认恢复手牌后交付。 |
| 正式验收成品 | `$loopseed one-shotted 交付可玩的切片，并独立验收存档、读档和重开。` | 对绑定版本的硬门槛和质量标杆完成独立验证，由严格模式生成验收记录。 |

## 在 Codex 里接着做

运行中的 Codex Goal 可以承载跨轮工作。支持 Goal 命令时，可用 `/goal $loopseed <愿景>` 直接启动。需要跨会话时，模型在项目的 `.loopseed.md` 留下愿景、已经观察到的变化和仍值得探索的问题。下次打开时从实际作品接着判断。用户叫停或额度用尽时让出控制权。[状态和恢复约定](skills/loopseed/references/state-contract.md#vision)

## 质量方法与严格交付

实际问题需要时，模型可以选择参考标杆、独立评审或盲测。显式选择 One-Shotted 后，按完整协议检查运行中的成品、绑定代码与产物，并独立验证。已有严格任务按原协议恢复。[质量方法](skills/loopseed/references/quality-methods.md) · [中文使用指南](docs/usage-guide.zh-CN.md) · [One-Shotted 协议](skills/loopseed/references/one-shotted-mode.md)

## 本地验证

```bash
python -m json.tool .codex-plugin/plugin.json >/dev/null
find skills/loopseed/schemas skills/loopseed/templates -name '*.json' -print0 \
  | xargs -0 -n1 python -m json.tool >/dev/null
python tools/verify_usage_guide_version.py
python -m compileall -q hooks skills/loopseed/scripts tests tools
python -m unittest discover -s tests -v
```

## 更详细说明

- [同一愿景的试玩对照与可玩版本](docs/reviews/v0.9.0-playtest/README.md)
- [生产使用技巧](docs/usage-guide.zh-CN.md)
- [One-Shotted 模式](skills/loopseed/references/one-shotted-mode.md)
- [锁定后的自治规则](skills/loopseed/references/autonomy-after-lock.md)
- [状态合同](skills/loopseed/references/state-contract.md)
- [Runtime Ladder](skills/loopseed/references/runtime-ladder.md)
- [致谢](ACKNOWLEDGEMENTS.md)

## License

MIT，见 [LICENSE](LICENSE)。
