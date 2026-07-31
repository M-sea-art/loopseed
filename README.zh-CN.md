# LoopSeed

**最小指令，最大有效自治；由证据决定停止。**

[English](README.md)

LoopSeed 是一个需要显式调用的 Codex Skill，用项目规划与直接证据驱动任务完成。`main` 上的稳定版仍是 0.3.0；C1.1 实验候选新增了正式项目绑定、机器执行证据、可恢复的 `BLOCKED`，以及验证过程中不可偷换产物的完整性检查。

## 生产使用技巧

先阅读 [LOOPSEED 生产使用技巧](docs/usage-guide.zh-CN.md)。该指南说明：

- 什么时候使用标准模式，什么时候使用 One-Shotted；
- 游戏项目和通用项目如何写紧凑、高杠杆目标；
- 稳定版与 C1.1 实验候选如何选择；
- 什么时候启用 Fresh Critic 或 Fan-out；
- 如何用最低成本获得真实运行证据；
- 哪些结果不能被当作完成证据。

这是一份与版本绑定的长期指南。每次 LoopSeed 升级都必须同步更新；CI 会检查指南版本与 `.codex-plugin/plugin.json` 是否一致。

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

“One‑Shotted”是**一次人类授权**，不是模型只回复一次。系统内部可以多轮规划、调用工具、运行测试、独立验收、修复、回滚、诚实阻塞，并凭新证据恢复；用户不需要反复说“继续”。

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

## 为什么它不是臃肿的多智能体框架

LoopSeed 的宗旨是减少重复提示与协调成本，而不是追求智能体数量。

- 一个 Lead 负责集成；
- 大规模实现前先声明验收门槛；
- 实现者不能审核自己的 Gate；
- Gate 失败必须进入 `REPAIR`，修复后重新验证；
- 连续两轮无进展，强制回到根因诊断并换路；
- 未解决的 P0/P1 缺陷禁止完成；
- 只有 Finalizer 可以写入 `VERIFIED`；
- 多写入者必须隔离，高耦合问题必须顺序收敛。

## One‑Shotted 控制面

初始化：

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

### 先绑定唯一验证对象

机器 Gate 执行前，先绑定项目、候选 Commit 和产物：

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py bind \
  --root . \
  --project PROJECT-P01 \
  --candidate "$(git rev-parse HEAD)" \
  --artifact dist/app.js
```

真实 Git 工作树中，CLI 会自行核对实际 `HEAD`。同一绑定可重复执行；若项目、Commit 或产物改变，必须开启新的 Run，不能静默换绑。

### 增加机器 Gate

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . \
  --id FLOW \
  --title "完整用户流程" \
  --criterion "新用户可以完成规定主流程" \
  --owner lead \
  --verifier verifier \
  --machine
```

`--machine` 表示手工写一句 `record PASS` 不能满足这个 Gate。

### 执行机器证据

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py run-evidence \
  --root . \
  --gate FLOW \
  --actor verifier \
  --command "python tools/playtest.py" \
  --project PROJECT-P01 \
  --candidate "$(git rev-parse HEAD)" \
  --artifact dist/app.js
```

机器 PASS 必须同时满足：

```text
命令退出码为 0
实际 Git HEAD 等于绑定 Commit（存在 Git 时）
绑定 Hash = 命令执行前 Hash = 命令执行后 Hash
```

如果验证命令在执行过程中修改或删除了被验证产物，系统会记录 `FAIL`；这条证据既不能通过 Gate，也不能解除阻塞。

### 进入 BLOCKED 并恢复

只有真实外部条件缺失时才进入阻塞：

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition \
  --root . \
  --blocker "独立验证环境暂不可用" \
  --unblock "验证命令可以实际运行"
```

条件成立后，针对同一绑定生成新的解阻证据：

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py run-evidence \
  --root . \
  --blocker <BLOCKER_ID> \
  --actor verifier \
  --command "python tools/check_unblock.py" \
  --project PROJECT-P01 \
  --candidate "$(git rev-parse HEAD)" \
  --artifact dist/app.js

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py resume \
  --root . \
  --evidence <EVIDENCE_ID> \
  --actor verifier
```

`resume` 只接受属于当前 Blocker、晚于阻塞时间、机器真实执行、绑定一致且产物完整性稳定的证据，然后把同一个 Run 恢复到 `ACTIVE / VERIFY`。

### 普通人工验收

不要求机器执行的 Gate 仍可由指定 Verifier 写入简洁证据：

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py record \
  --root . \
  --gate COPY_REVIEW \
  --result PASS \
  --actor verifier \
  --summary "已核对批准文案"
```

### 终局判断

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py finalize --root .
```

以下任一条件不满足都会拒绝完成：所有必需 Gate 有合法证据；机器 Gate 始终绑定同一个产物；当前 Git 与 Artifact 仍匹配；合同与证据账本一致；不存在开放的 P0/P1 缺陷。

完整协议见 [One‑Shotted Mode](skills/loopseed/references/one-shotted-mode.md)。

## Hooks

- `SessionStart` 只为 ACTIVE 状态恢复压缩上下文；
- One‑Shotted JSON 状态优先于旧 `.loopseed.md`；
- `Stop` 在验收未完成时只请求一次续接；
- `VERIFIED`、`BLOCKED`、`ABORTED` 允许当前会话停止；
- `BLOCKED` 不是自动完成，也不是永久死锁，只能通过显式 `resume` 和新鲜机器证据恢复。

Hooks 不会扩大权限、自动开放网络，也不会假装当前执行环境具备不存在的能力。

## 本地验证

```bash
python -m json.tool .codex-plugin/plugin.json >/dev/null
find skills/loopseed/schemas skills/loopseed/templates -name '*.json' -print0 \
  | xargs -0 -n1 python -m json.tool >/dev/null
python tools/verify_usage_guide_version.py
python -m compileall -q hooks skills/loopseed/scripts tests tools
python -m unittest discover -s tests -v
```

## 关键文档

- [生产使用技巧](docs/usage-guide.zh-CN.md)
- [One‑Shotted 模式](skills/loopseed/references/one-shotted-mode.md)
- [状态合同](skills/loopseed/references/state-contract.md)
- [运行机制阶梯](skills/loopseed/references/runtime-ladder.md)
- [执行卡片](skills/loopseed/references/playbook.md)
- [版本管理](docs/version-management.md)

## License

MIT. See [LICENSE](LICENSE).
