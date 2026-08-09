# LoopSeed

**对话求准，一击点火，并行加速，证据决定完成。**

[English](README.md)

LoopSeed 是一个需要显式调用的、**以游戏开发为主场的 AI 生产发动机**。

它允许玩家先从一个还不完整的游戏设想开始。模型通过多轮共创对话理解、修正、放大、补全并延续这个设想；当方向足够精准后，用户一次授权，系统进入不中断的 One‑Shot 生产，通过受控 Fan‑out 并行完成设计、程序、资产、整合、试玩与验证。

它也可以通过较轻的领域适配器用于网站、应用、工具和其他通用项目。

```text
玩家的创意种子
      ↓
创意共导演对话
保留 · 修正 · 放大 · 补全 · 延续 · 提供选项
      ↓
用户授权的创意简报
      ↓
One‑Shot 正式点火
      ↓
受控 Fan‑out 并行生产
      ↓
整合 · 试玩 · 视觉审查 · 性能验收
      ↓
VERIFIED / BLOCKED / FAIL 证据
```

LoopSeed 同时追求两件事：

- **愿景上敢放大**：对话可以把最有生命力的体验推到更高；
- **验收上不吹牛**：最终结论绝不能超过真实证据。

## 两种执行方式

### 标准 LoopSeed

```text
$loopseed <目标>
```

使用足以闭环的最低成本循环：

```text
探索 → 行动 → 观察 → 验证 → 调整
```

默认只有一个主线程、一个写入者和一个集成路径。

### One‑Shotted 生产

```text
$loopseed one-shotted <一句自然语言目标>
```

这里的“One‑Shotted”是**一次正式生产授权**，不等于只能有一条用户消息，也不等于模型只能回复一次。

游戏设想通常会先经过创意共导演对话。创意简报一旦由用户授权并锁定，系统就会自主规划、实现、分派真正独立的任务、整合、运行测试、采集证据、修复缺陷并完成终局判断，不再反复要求用户说“继续”。

## 游戏优先的创意共导演

用户不需要一开始就写出完整策划案。

在对话中，模型可以：

- **保留**游戏最初的灵魂和已经认可的决定；
- **修正**互相冲突或会削弱产品的设想，并说明取舍；
- **放大**最独特、最值得展示的玩家体验；
- **补全**缺失的玩法与产品逻辑；
- **延续**用户已经认可的方向，不在下一轮重新归零；
- 在存在真正选择时，提供 **2–4 个有明显区别的选项**，推荐其中一个，并说明各自后果。

每一轮对话都必须推进一个会改变产品结果的重要决策。不得重复已经回答的问题，不得询问仓库里已有的事实，不得把可逆的底层实现细节推给用户，也不得悄悄把用户要的游戏改成更容易实现的场景、后台、静态页面或几何 Blockout。

默认最多五轮模型问题，但这是上限，不是任务量。方向清楚后应立即锁定，不为显得认真而继续盘问。

## 三种生产档位

### Focused｜精准交付

快速完成最小但完整的结果，不主动扩张产品设想。

### Studio｜游戏工作室

游戏项目的默认生产档位。目标是一份可公开展示、整体统一的垂直切片，包含游戏身份、美术圣经、游戏感、资产、完整流程、视觉证据与性能门槛。

### Moonshot｜狂野工作室

主动放大最强体验，并对真正独立的质量面进行更积极的 Fan‑out。

Moonshot 必须同时写明：

- 想把哪项体验推得更惊人；
- 用什么范围护栏阻止功能无限膨胀。

Moonshot 是把一个核心体验做深，不是无节制堆系统；可以放大愿景，不能放大完成结论。

## 初始化

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py init \
  --root . \
  --goal "制作一个真正活着的武侠门派经营垂直切片"
```

可选参数：

```text
--domain auto|game|general
--production-mode auto|focused|studio|moonshot
--dialogue auto|on|off
--max-dialogue-rounds 1..8
```

默认行为：

- 识别为游戏时进入 `CALIBRATE`；
- 通用项目默认以 Focused 路线进入 `BIND`；
- 可以显式要求 Moonshot、开启对话或在合同已经非常清楚时关闭对话。

## 记录一轮共创选择

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py dialogue-turn \
  --root . \
  --actor model \
  --kind question \
  --summary "选择首个切片怎样证明门派真的活着" \
  --effect preserve \
  --effect amplify \
  --advance core_loop \
  --advance hero_moment \
  --option "A|三日门派危机|用一个完整经营循环证明人物自主性" \
  --option "B|电影化场景|视觉更强，但玩法证据较弱" \
  --option "C|大型沙盒|内容更广，但完成风险更高" \
  --recommended A
```

记录用户的自然语言回答，把已接受的决定编译为创意简报，然后锁定：

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py lock-brief \
  --root . \
  --file creative-brief.json
```

锁定后生成：

- `creative-brief.json`：结构化生产权威；
- `compiled-shot.md`：人类可读的一击生产简报。

状态从 `CALIBRATE` 进入 `BIND`。在用户授权的创意简报锁定之前，不能声明生产验收 Gate，也不能用普通状态切换绕过去。

## 游戏生产合同

游戏创意简报会定义适用的内容，包括：

- 玩家承诺与玩家身份；
- 核心循环与世界回应；
- 独特机制；
- 美术方向与游戏感；
- 英雄时刻与垂直切片边界；
- 资产路线与占位资产替换条件；
- 完整试玩、成功、失败和重开；
- 固定镜头与角色/场景独立审查；
- FPS、帧时间、Draw Calls、三角形、内存、加载、构建、打包与重启；
- 禁止替代结果：静态场景、普通 Dashboard、能跑的空壳和几何 Blockout 都不能冒充完成游戏。

通用项目使用同一证据发动机，但切换为相应的产品、流程、产物、质量与性能合同。

## 受控 Fan‑out

Fan‑out 是涡轮增压，不是多智能体表演。

只有当任务真正独立、能够分别验收、写入范围隔离、并行确实更快且可以由一个 Lead 收敛时，才允许并行。适合的对象包括独立资产族、只读调查、独立测试、音频、边界清楚的 UI 和性能分析。

以下内容若存在耦合，必须由单一负责人顺序掌控：

- 产品身份；
- 核心循环与共享游戏状态；
- 技术架构；
- 全局灯光和后处理；
- 最终构图；
- 整体集成；
- 最终放行。

> Fan‑out 工作，不 Fan‑out 对游戏的不同理解。

### 不空等调度

非简单 Fan‑out 会写入一个很小的 `task-graph.json`，由运行时计算当前“最大安全可执行批次”。任务关系只有三类：

- `HARD_DEPENDENCY`：只阻塞它的直接消费者；
- `SOFT_ADVICE`：顾问意见，不得阻塞 Builder；
- `INDEPENDENT`：写入边界安全时可以并行。

汇合点显式选择 `FIRST_SUCCESS`、`QUORUM` 或 `ALL_REQUIRED`。只要还有安全可执行任务，系统就拒绝等待。共享写入范围保持单写者；不同 Worktree 可以并行。Lead 派出子智能体后仍然负责调度，不能变成“派活—等回信”。

## 证据驱动的完成

创意简报锁定之后：

```text
BIND → PLAN → IMPLEMENT → VERIFY
                       失败 ↓    ↓ 通过
                          REPAIR → VERIFY → FINALIZE
```

- 大规模实现前先声明验收标准；
- 实现者不能审核自己的 Gate；
- Gate 失败必须修复并重新验证；
- 连续两轮无进展，强制回到根因诊断并换路；
- 未解决的 P0/P1 缺陷禁止完成；
- 只有 Finalizer 可以写入 `VERIFIED`；
- `BLOCKED` 必须写清真实外部阻塞和精确解除条件；
- 低质量、测试失败或第一条路线走不通都不是停止借口，而是修复信号。

### 真实性桥

实现完成后，LoopSeed 会另外冻结一份 `verification_binding`，把真实 Git HEAD 与一个稳定交付产物绑定。绑定前必须先提交候选代码和验证器代码：受 Git 跟踪的产品内容必须与 HEAD 一致；未被 Git 忽略的未跟踪内容，只能是绑定产物或当前已哈希证据产物。`.loopseed` 控制数据和被 Git 忽略的环境/构建内容不参与这项洁净检查，因此验证流程不得依赖可变的、被忽略的源码。

机器 Gate 必须由证据 Runner 真正执行命令，并记录退出码、超时、有界输出、HEAD、工作树洁净状态，以及执行前后的产物 SHA‑256。不同 Gate 的验证命令可并行执行，收据通过短事务合并。人工或视觉 PASS 必须引用项目内真实存在的截图、录像或报告，并在记录时计算哈希。把命令写进说明文字，不算执行证据。

如果返修改变了候选产物，新一代绑定会归档旧候选并重置旧 Gate 的 PASS。所有必需任务只能以 `SUCCEEDED` 进入终局；optional 任务也必须明确收口，被淘汰的实验候选通常应设为 `CANCELLED`。

## 控制面

```text
.loopseed/one-shotted/
├── project-identity.md
├── architecture-contract.md
├── goal-contract.json
├── creative-brief.json
├── compiled-shot.md          # 创意锁定后生成
├── dialogue.jsonl
├── acceptance.json
├── expert-registry.json
├── task-graph.json
├── state.json
├── evidence.jsonl
├── defects.jsonl
└── final-report.json         # 只有最终验证通过后生成
```

控制面只保存紧凑的决定与证据，不保存私密推理或秘密信息。

## 增加并验证 Gate

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . \
  --id FLOW \
  --title "完整游戏循环" \
  --criterion "新玩家能够完成、失败并重新开始规定的垂直切片" \
  --owner lead \
  --verifier verifier \
  --machine

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition \
  --root . --phase PLAN --next "规划有边界的实现"
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition \
  --root . --phase IMPLEMENT --next "构建并提交候选版本"

# 在这里运行项目自己的构建命令，然后提交候选代码和验证器代码。
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition \
  --root . --phase VERIFY --next "冻结并验证候选版本"

head="$(git rev-parse HEAD)"
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py bind \
  --root . \
  --project "my-game" \
  --candidate "$head" \
  --artifact build/game.zip

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py run-evidence \
  --root . \
  --gate FLOW \
  --actor verifier \
  --command "python tools/playtest.py" \
  --project "my-game" \
  --candidate "$head" \
  --artifact build/game.zip
```

人工或视觉 Gate 使用 `record --artifact captures/flow-pass.mp4`；文件必须真实存在于项目内，并持续接受哈希复核。

### 从 v0.7 升级

- ACTIVE 的 v0.7 run 可以继续；首次执行 v0.7.1 `bind` 时，会重置绑定前的旧 PASS，随后必须用 `run-evidence` 或已哈希产物重新验证。
- `record --command` 会被明确拒绝，因为旧入口从未执行命令；请改用 `bind` + `run-evidence`。
- 旧 `FIRST_SUCCESS`/`QUORUM` 中已取消但默认 required 的候选臂，可运行 `task-requirement --task <ID> --optional --actor lead --summary "legacy candidate arm"` 迁移。
- 已经是 `VERIFIED` 的 v0.7 run 只保留为旧版、未证明真实性的历史收据。若需要 v0.7.1 完整性收据，请新建 run；系统不会静默重签旧终态。

## 终局判断

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py finalize --root .
```

以下任一条件不满足都会拒绝完成：创意锁有效；当前验证绑定没有漂移；所有必需任务均为 `SUCCEEDED`；所有 optional 任务也已明确收口；至少存在一个必需 Gate；所有必需 Gate 均有真实机器证据或已哈希人工产物证据；合同与证据引用一致；不存在仍开放的 P0/P1 缺陷。终局报告还必须与当前 run、Gate、证据、任务、绑定和时间戳逐项一致。

完整协议见 [One‑Shotted Mode](skills/loopseed/references/one-shotted-mode.md)。

## 为什么它不是臃肿的多智能体框架

LoopSeed 优化的是协调成本，而不是 Agent 数量：

- Focused 使用足够完成目标的最小拓扑；
- Studio 只激活垂直切片真正需要的生产角色；
- Moonshot 对独立质量面积极并行，但始终保留一个游戏身份与一个集成负责人；
- 调度器追求最大安全可执行批次，而不是最大 Agent 数量；顾问软建议不得造成主线空等；
- 状态只在决定、证据、换路、阻塞和终局时更新，不记录每个念头和工具调用。

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
