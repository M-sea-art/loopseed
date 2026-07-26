# LoopSeed

**最小指令，最大有效自治；由证据决定停止。**

[English](README.md)

LoopSeed 是一个需要显式调用的 Codex Skill，用项目规划与直接证据驱动任务完成。0.3 新增 **One‑Shotted 模式**：用户只给出一次自然语言授权，系统即可自主完成规划、实现、独立验收、修复和终局判断，不需要用户不断重复“继续”。

## 两种模式

### 标准 LoopSeed

```text
$loopseed <目标>
```

使用足以闭环的最低成本循环：

```text
探索 → 行动 → 观察 → 验证 → 调整
```

默认只有一个主线程、一个写入者和一个集成路径。只有证据证明值得时，才增加状态接力、子智能体、Worktree、Hooks 或定时恢复。

### One‑Shotted 模式

```text
/goal $loopseed one-shotted <一句自然语言目标>
```

或：

```text
$loopseed one-shotted <一句自然语言目标>
```

这里的“One‑Shotted”是**一次人类授权**，不是模型只回复一次。系统内部可以多轮规划、调用工具、分派真正独立的任务、运行测试、采集证据、修复缺陷、回滚回归并从状态恢复；但不再要求用户反复推动。

```text
一次人类目标
      ↓
项目身份 + 架构合同
      ↓
可观察验收门槛
      ↓
规划 → 实现 → 独立验证
             失败 ↓      ↓ 通过
                修复 → 再验证
                         ↓
                      终局门
```

它复刻的是优秀“one-shot”项目真正有效的工程方法：提示词只负责点火；架构合同、所有权边界、可重复证据、独立批评者和严格停止条件，才让任务能够自我驱动。

## 为什么它不是臃肿的多智能体框架

LoopSeed 的宗旨是减少重复提示与协调成本，而不是追求智能体数量。

- 一个 Lead 负责集成；
- 大规模实现前先声明验收门槛；
- 实现者不能审核自己的 Gate；
- Gate 失败必须进入 `REPAIR`，修复后重新验证；
- 连续两轮无进展，强制回到根因诊断并换路；
- 未解决的 P0/P1 缺陷禁止完成；
- 只有 Finalizer 可以写入 `VERIFIED`；
- 多写入者必须隔离，高耦合问题必须由单一负责人顺序收敛。

## One‑Shotted 控制面

内置的零依赖 CLI 会在目标项目中建立一个小型、可审计的控制面：

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py init \
  --root . \
  --goal "完成用户要求的完整垂直切片"
```

生成：

```text
.loopseed/one-shotted/
├── project-identity.md
├── architecture-contract.md
├── goal-contract.json
├── acceptance.json
├── expert-registry.json
├── state.json
├── evidence.jsonl
├── defects.jsonl
└── final-report.json       # 只有终局验证通过后才生成
```

### 增加验收 Gate

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . \
  --id FLOW \
  --title "完整用户流程" \
  --criterion "新用户可以完成文档规定的主流程" \
  --owner lead \
  --verifier verifier
```

### 记录独立验收

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py record \
  --root . \
  --gate FLOW \
  --result PASS \
  --actor verifier \
  --summary "完整主流程实际运行通过" \
  --command "python tools/playtest.py"
```

### 终局判断

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py finalize --root .
```

以下任一条件不满足都会拒绝完成：至少存在一个必需 Gate；所有必需 Gate 均有指定 Verifier 写入的 PASS 证据；合同与证据引用一致；不存在仍开放的 P0/P1 缺陷。

完整协议见 [One‑Shotted Mode](skills/loopseed/references/one-shotted-mode.md)。

## Hooks

现有 Hooks 保持保守：

- `SessionStart` 只为 ACTIVE 状态恢复压缩上下文；
- One‑Shotted JSON 状态优先于旧 `.loopseed.md`；
- `Stop` 在验收未完成时只请求一次续接；
- `stop_hook_active` 防止递归循环；
- `VERIFIED`、`BLOCKED`、`ABORTED` 必定允许停止。

Hooks 不会扩大权限、自动开放网络，也不会假装当前 Codex 表面具备不存在的机制。

## 本地验证

```bash
python -m json.tool .codex-plugin/plugin.json >/dev/null
find skills/loopseed/schemas skills/loopseed/templates -name '*.json' -print0 \
  | xargs -0 -n1 python -m json.tool >/dev/null
python -m compileall -q hooks skills/loopseed/scripts tests
python -m unittest discover -s tests -v
```

## 关键文档

- [One‑Shotted 模式](skills/loopseed/references/one-shotted-mode.md)
- [状态合同](skills/loopseed/references/state-contract.md)
- [运行机制阶梯](skills/loopseed/references/runtime-ladder.md)
- [执行卡片](skills/loopseed/references/playbook.md)

## License

MIT. See [LICENSE](LICENSE).
