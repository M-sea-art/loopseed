# LoopSeed

**目标。标杆。构建。比较。只修最大差距。再来一轮。**

[English](README.md)

LoopSeed v0.8 是一个需要显式调用的、**以游戏开发为主场的 AI 生产运行时**。它围绕一个极简单的原则重新组织：

> **Gate 是地板，Bar 是天花板。**

测试通过、项目能构建、阶段合同满足，只能证明“它没有坏”。这些都不能单独证明“它已经足够好”。

所以 v0.8 把一个很小的 Gauntlet 式质量循环放在生产中心，把上下文恢复、调度、证据、完整性和断点续跑放到下面作为支撑 Shell。

```text
目标 GOAL
   ↓
最强可检验标杆 BAR
   ↓
Agent 自主拆解
   ↓
做出真实产物
   ↓
看 · 玩 · 跑 · 测
   ↓
Fresh Critic 独立评审
   ↓
适合时做盲测 / 等价 A-B
   ↓
只找一个：当前最大剩余差距
   ↓
修复 · 再比较 · 胜者留下
   ↺
```

v0.8 不能再因为“工程 Gate 全绿”就写入 `VERIFIED`。真正完成必须同时拥有当前、独立、可追溯的两类证据：

1. **Hard Floor｜硬门槛**：产品真的能工作，并满足不可妥协的约束。
2. **Quality Bar｜质量标杆**：真实输出达到或击败选定的可检验标准。

---

## LoopSeed 为什么存在

今天的编码 Agent 已经很擅长“做出一个能跑的东西”。更难的问题是：

> **怎样阻止它在第一个看起来合理的版本上停手？**

最典型的失败链是：

```text
用户要：成品游戏 / 高质量产品
        ↓
Agent 做：技术上成立的原型
        ↓
测试通过
        ↓
Agent 宣布完成
```

LoopSeed 把目标函数改成：

```text
能不能跑？               → 地板
合同满足吗？             → 地板
真实结果面对标杆还输吗？ → 质量裁决
```

整个系统明确分成两层。

### Seed Kernel｜种子内核

这是 Agent 最应该把注意力放在上面的质量优化器：

```text
Goal → Bar → Build → Inspect → Critic → Biggest Gap → Repair → Compare Again
```

### Runtime Shell｜运行时外壳

这些能力继续保留，但它们只负责保护循环，不负责替代循环：

- 恢复已有项目的规划、意图和已定决定；
- 只在真正存在产品歧义时使用 Creative Dialogue；
- 保持一个产品身份和一个最终集成负责人；
- 只 Fan-out 真正可以独立验收的工作；
- 还有安全可执行任务时禁止空等；
- 把验证绑定到真实 Git HEAD 和产物 SHA-256；
- PASS 必须有独立、真实、产物化证据；
- 修复改变候选后，旧 PASS 自动失效；
- 保存可恢复的 durable state；
- 宁可拒绝完成，也不制造“已经完成”的幻觉。

一句话：

> **Shell 是护甲，不是方向盘。**

---

## 最快开始

### 小而明确的任务

```text
$loopseed <目标>
```

使用足以闭环的最低成本循环：

```text
探索 → 行动 → 观察 → 验证 → 调整
```

默认一个主线程、一个写入者、一个集成路径。

### 完整自主生产

```text
$loopseed one-shotted <一句自然语言目标>
```

例如：

```text
$loopseed one-shotted 把当前武侠山崖门派原型做成真正活着的、手工微缩感的经营游戏。
选择你实际能够查看和比较的最强现实标杆，生产路线由你自己决定。每轮检查真实运行结果，
交给 fresh critic 独立批评，只修当前最大的一个剩余差距；硬门槛和质量 Bar 都获得独立证据之前，
不要宣布完成。
```

“One-Shotted”表示**一次正式生产授权**，不是一条模型回复。

当目标已经足够清楚后，LoopSeed 应该自己持续构建、观察、修复、重新验证，而不是隔几步回来问一句“要不要继续”。

你不需要先写一份巨大的 GDD 或 PRD。最有价值的输入通常只有两样：

- **你真正想得到什么；**
- **什么现实对象或可测指标代表“这次真的做到了”。**

---

## Bar 到底是什么

Bar 必须是 Agent **真的可以查看、执行或测量**的标准。

好的 Bar：

- 一张锁定的参考截图，对比同机位真实游戏帧；
- 一个现实游戏/产品流程，在等价条件下直接比较；
- 一个确定性的试玩目标；
- FPS、帧时间、延迟、准确率等可测阈值；
- fresh critic 的盲 A/B 偏好；
- 同一任务里，候选必须胜过 incumbent。

弱 Bar：

- “做得高级一点”；
- 没有现实参照的“AAA 品质”；
- “看起来不错”；
- 只看源代码、不看真实产物的自我评价。

如果用户没有给 Bar，Lead 应该主动寻找或提出**最强、最具体、实际可检验**的标准，而不是补一句模糊的形容词。

### Gate 与 Bar 的区别

**Hard Floor**问的是“这个产品成立吗？”：

- 能构建；
- 完整流程可走通；
- 成功、失败、重开存在；
- 性能不越预算；
- 必需内容齐全；
- 没有开放 P0/P1。

**Quality Bar**问的是“这个产品够好吗？”：

- 同条件盲 A/B 中，真实画面能否胜过参考？
- 交互是否比 incumbent 更清楚、更灵敏？
- 最终产物是否真的达到命名的生产标准？

v0.8 把两者都变成一等运行时 Gate Role。

```bash
# Hard Floor：硬门槛
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . \
  --id FLOW \
  --title "完整流程" \
  --criterion "新玩家可以完成、失败并重新开始规定切片" \
  --owner lead \
  --verifier flow-verifier \
  --machine

# Quality Bar：质量标杆
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . \
  --id BAR \
  --title "参考比较" \
  --criterion "等价盲 A/B 中，fresh critic 更偏好候选而不是锁定参考" \
  --owner lead \
  --verifier visual-critic \
  --bar
```

v0.8 的 `VERIFIED` 至少要求一个 required hard-floor gate 和一个 required quality-bar gate。

---

## Critic 必须看真实产物

Critic 不是来给 Builder 的解释打分。

它必须检查产品本身。

| 你声称什么 | 至少要看什么 |
|---|---|
| 视觉质量 | 截图 / 视频 / 真实运行帧 |
| 交互质量 | 实际试玩 / Runtime 检查 |
| 性能 | 测量数据 |
| 构建正确 | 真正执行的命令 |
| 产品流程 | 完整真实流程 |
| 比标杆更强 | 直接等价比较 |

Critic 每轮优先只返回：

> **当前最大的一个材料性差距是什么？**

这样 Repair Loop 才不会被一长串“建议清单”重新拖成项目管理会议。

适合盲 A/B 时，初始 verdict 应隐藏 Builder 的历史解释、自我辩护和“我觉得已经很好了”。

---

## 新项目与已有项目

### 新项目

从 Goal 开始。

只有当真正存在一个会改变最终产品结果的歧义，才需要校准。

游戏目标仍可能进入 `CALIBRATE`，但它不是“必须问满几轮”的访谈任务。如果当前想法已经足够精准，应该直接综合并锁定，而不是为了显得认真继续盘问。

### 已有项目

LoopSeed 会先寻找并恢复可能具有权威性的规划来源，例如：

- `README` / `AGENTS.md`；
- GDD 与产品规格；
- Roadmap 与 Milestone；
- design / planning / decision records。

已经定下来的决定继承，不重新问。

**Context Recovery 与 Creative Dialogue 已经解耦。** 即使显式使用 `--dialogue off`，只要已有项目中发现规划来源，生产仍必须先恢复上下文。

如果已有项目真的没有找到任何可能的规划源，Runtime 会写下 `NONE_FOUND` receipt，然后继续，不凭空制造一个人工审批 Gate。

---

## Creative Dialogue 的新位置

Creative Dialogue 是**校准工具**，不是生产发动机。

只用来处理真正会改变产品结果的问题。模型可以：

- 保留已经接受的产品身份；
- 澄清实质歧义；
- 修正互相冲突的决定；
- 放大最值得追求的体验；
- 补全缺失的产品逻辑；
- 延续前面已经接受的决定；
- 必要时给出 2–4 个真正不同的选项，并推荐一个。

不要问：

- 仓库里已经有答案的事实；
- 可逆的底层实现细节；
- 已有项目规划已经明确的决定。

创意简报一旦锁定，普通生产判断重新交还自治循环。

弱截图、测试失败、Critic FAIL 都意味着：

> **Repair。**

而不是：

> “要不要继续？”

---

## 受控 Fan-out

Fan-out 是加速器，不是多智能体仪式。

适合并行：

- 独立资产族；
- 只读调查；
- 独立测试；
- 音频；
- 边界清楚的 UI；
- 性能分析。

强耦合内容保持一个负责人：

- 产品身份；
- 核心循环；
- 共享 Runtime State；
- 架构；
- 全局构图 / 灯光；
- 最终集成。

> **Fan-out 工作，不 Fan-out 对产品的不同理解。**

非简单任务使用 `task-graph.json` 明确三种关系：

- `HARD_DEPENDENCY`；
- `SOFT_ADVICE`；
- `INDEPENDENT`。

只要还有安全可执行任务，Scheduler 就拒绝等待。共享写入范围保持单写者；隔离 Worktree 可以并行。

---

## 证据与完整性

实现后，LoopSeed 冻结 `verification_binding`：

```text
真实 Git HEAD
+ 稳定交付产物 SHA-256
+ 当前 binding generation
```

机器 Gate 必须由 Evidence Runner 真执行。写在说明里的命令，不算证据。

视觉、体验等 observational PASS 必须指向真实项目内产物，例如：

- 截图；
- 录像；
- 报告。

记录时会哈希。

如果 Repair 改变候选：

1. 旧候选进入历史；
2. 创建新的 binding generation；
3. 旧 PASS 失效；
4. 相关 Gate 重新验证。

这样，一张旧截图不能替一份新 Build 作证。

---

## 生产状态机

```text
CALIBRATE → BIND → PLAN → IMPLEMENT → VERIFY
                                  FAIL ↓    ↓ PASS
                                     REPAIR → VERIFY → FINALIZE
```

终局很严格：

- `VERIFIED`：Hard Floor 和 Bar 都有当前证据，必需工作完成，没有阻塞缺陷；
- `BLOCKED`：存在一个 Runtime 自己无法解决的精确外部条件，并写明解除条件；
- `ABORTED`：Owner 明确停止。

低质量、测试失败、不确定、第一条路线走不通，都不叫 BLOCKED。

它们触发：

```text
修复 / 回滚 / 重规划
```

连续两轮没有材料性进展，强制进行根因重规划，并换一条实质不同的路线。

---

## 控制面

```text
.loopseed/one-shotted/
├── project-identity.md
├── project-context.json
├── architecture-contract.md
├── goal-contract.json
├── creative-brief.json
├── compiled-shot.md
├── dialogue.jsonl
├── acceptance.json
├── expert-registry.json
├── task-graph.json
├── state.json
├── evidence.jsonl
├── defects.jsonl
└── final-report.json
```

这里保存的是紧凑的决定和证据，不是私密思维链日志。

---

## 最小验证闭环

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py init \
  --root . --goal "<goal>"

# 大规模实现前，至少声明一个 Hard Floor 和一个 Bar。
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . --id FLOW --title "Flow" --criterion "<可观察硬门槛>" \
  --owner lead --verifier verifier --machine

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . --id BAR --title "Quality Bar" --criterion "<直接比较规则>" \
  --owner lead --verifier critic --bar

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition \
  --root . --phase PLAN --next "规划最小但有机会赢的路线"
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition \
  --root . --phase IMPLEMENT --next "构建候选"
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition \
  --root . --phase VERIFY --next "冻结并检查真实输出"

head="$(git rev-parse HEAD)"
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py bind \
  --root . --project "my-project" --candidate "$head" --artifact build/output.zip

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py run-evidence \
  --root . --gate FLOW --actor verifier --command "python tools/verify.py" \
  --project "my-project" --candidate "$head" --artifact build/output.zip

# 观察型 Bar：独立 Critic 必须记录真实哈希产物。
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py record \
  --root . --gate BAR --result PASS --actor critic \
  --summary "候选赢得锁定的等价比较" \
  --artifact captures/blind-ab-result.png

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py finalize --root .
```

---

## 三种生产档位

- **Focused**：最小但完整，使用最少必要拓扑。
- **Studio**：面向可公开展示的游戏/产品垂直切片，启用真正需要的质量学科。
- **Moonshot**：提高体验上限，但必须同时锁定 scope guard。

更高档位不等于更多仪式。

它只意味着：

> **当 Bar 值得时，允许投入更高的质量野心。**

---

## 成本纪律

LoopSeed 的升级顺序应该永远是：

```text
一个线程足够       → 不 Fan-out
一次真实比较足够   → 不造评审官僚系统
一个 Critic 足够   → 不建评审委员会
机器证据足够       → 不用说明文字代替
```

两条治理原则继续保留：

> **No new mechanism without demonstrated product effect.**
>
> 没有证明能让产品结果更好的机制，不进入核心。

> **Every new control must replace more uncertainty than complexity it introduces.**
>
> 新控制消除的不确定性，必须大于它增加的复杂度。

---

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

- [生产使用技巧](docs/usage-guide.zh-CN.md)
- [One-Shotted 模式](skills/loopseed/references/one-shotted-mode.md)
- [锁定后的自治规则](skills/loopseed/references/autonomy-after-lock.md)
- [状态合同](skills/loopseed/references/state-contract.md)
- [Runtime Ladder](skills/loopseed/references/runtime-ladder.md)
- [致谢](ACKNOWLEDGEMENTS.md)

## License

MIT，见 [LICENSE](LICENSE)。
