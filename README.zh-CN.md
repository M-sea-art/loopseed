# LoopSeed

**目标。标杆。真机运行。比较。只修最大差距。再来一轮。**

[English](README.md)

LoopSeed v0.8.1 是一个需要显式调用的、**以游戏开发为主场的 AI 生产运行时**。

> **Gate 是地板，Bar 是天花板。**

测试通过、项目能构建、阶段合同满足，只能证明“它有资格被评价”，不能单独证明“它已经足够好”。

所以 LoopSeed 把一个很小的 Gauntlet 质量循环放在生产中心，把上下文恢复、调度、证据、完整性和断点续跑压到后台作为 Runtime Shell。

```text
目标 GOAL
   ↓
最强可检验 BAR
   ↓
Agent 自主拆解
   ↓
做出真实产物
   ↓
启动 · 玩 · 看 · 测
   ↓
Fresh Critic 第一手评审
   ↓
适合时盲测 / 等价 A-B
   ↓
只找一个：当前最大剩余差距
   ↓
修复 · 再运行 · 再比较 · 胜者留下
   ↺
```

v0.8+ 不能再因为“工程 Gate 全绿”就写 `VERIFIED`。真正完成至少同时需要：

1. **Hard Floor｜硬门槛**：产品真的能工作，并满足不可妥协的约束；
2. **Quality Bar｜质量标杆**：真实输出达到或击败选定的可检验标准。

---

## v0.8.1：开始评价用户真正看到、听到、玩到的东西

这次没有再加新框架，而是把四条生产规则收紧为 Kernel Invariant。

### 1. 游戏需要在运动中判

如果你要判断的是：

- 动画；
- 镜头运动；
- 战斗阅读性；
- 尺度感；
- 尘土/粒子；
- 输入反馈；
- 节奏；
- game feel；

那么一张漂亮截图不能证明 PASS。

```text
Still-image win ≠ Motion win
```

涉及动态质量时，必须看录像、真实 Runtime 或试玩过程。

### 2. Critic 尽量第一手观察

环境允许时，Fresh Critic 自己：

```text
启动真实 Build
  ↓
玩 / 操作 / 浏览
  ↓
自己截图、录片段、做测量
  ↓
和冻结的 Bar 比较
```

Critic 不应该把 Builder 精挑的几张截图和“我已经修好了”的解释当主要证据。

如果 Critic 无法访问 Runtime，必须说清楚限制；此时不能靠静态截图推断 motion、interaction 或 game feel 已经通过。

### 3. 生成资产必须进产品里判

角色、模型、精灵、特效、动画、材质的独立 Render 可以做 sanity check，但不能单独获得最终产品质量 PASS。

只要这些因素会影响结果，就必须放进真实：

```text
相机 + 比例 + 灯光 + UI + 动画 + Runtime 状态
```

再判断。

> **Asset Quality 最终要变成 Asset-in-Product Quality。**

### 4. 大规模 Fan-out 后必须重新整体化

局部都更漂亮，不代表整个产品更统一。

每轮主要并行改善结束后：

```text
合并局部赢家
  ↓
一个 Fresh Whole-Product Critic
  ↓
找一个最大的跨模块不一致
  ↓
先修整体一致性
  ↓
再开下一轮大规模 Fan-out
```

Fan-out 改进零件，Whole-Product Critic 确保这些零件仍属于同一个游戏。

---

## 为什么需要 LoopSeed

今天的编码 Agent 已经很擅长“做出一个能跑的东西”。更难的是阻止它在第一个合理版本上停手。

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
能不能跑？               → Hard Floor
合同满足吗？             → Hard Floor
真实结果面对 Bar 还输吗？ → Quality Decision
```

系统只有两层。

### Seed Kernel｜种子内核

```text
Goal → Bar → Build → Run → Fresh Critic → Biggest Gap → Repair → Compare Again
```

这是 Agent 最应该把注意力放在上面的部分。

### Runtime Shell｜运行时外壳

继续负责：

- 恢复已有项目规划与已定决定；
- 只在真正有产品歧义时使用 Creative Dialogue；
- 保持一个产品身份与最终集成负责人；
- 只 Fan-out 可独立判断的工作；
- 有安全任务可做时禁止空等；
- 把验证绑定到真实 Git HEAD 与 Artifact SHA-256；
- PASS 必须有独立、真实、产物化证据；
- Repair 改变候选后让旧 PASS 失效；
- 保存可恢复状态；
- 宁可拒绝完成，也不制造完成幻觉。

> **Shell 是护甲，不是方向盘。**

---

## 最快开始

### 小而明确的任务

```text
$loopseed <目标>
```

默认走足以闭环的最低成本路径：

```text
探索 → 行动 → 观察 → 批评 → 调整
```

### 完整自主生产

```text
$loopseed one-shotted <一句自然语言目标>
```

例如：

```text
$loopseed one-shotted 把当前武侠山崖门派原型做成真正活着的手工微缩经营游戏。
选择你实际能够查看和比较的最强现实 Bar；如果没有有意义的现实对应物，先冻结一个生成的
Synthetic Bar。生产路线由你自己决定。Critic 必须尽量亲自运行真实 Build；涉及运动的质量要
在运动中判，生成资产放进真实场景里判。每轮只修最大的一个剩余差距；硬门槛和 Bar 都获得
独立证据之前不要宣布完成。
```

“One-Shotted”表示**一次正式生产授权**，不是只允许模型回复一次。

方向清楚后，LoopSeed 应该自己持续构建、运行、批评、修复和重新验证，而不是隔几步回来问“要不要继续”。

---

## Bar 分三种

Bar 必须是 Agent **真的可以查看、运行或测量**的标准。

### Real Bar｜现实标杆

现实中有有意义的对应物时优先用它：

- 真实游戏 / 产品；
- reference frames / clips；
- incumbent build；
- benchmark；
- 可测目标。

### Synthetic Bar｜生成标杆

如果你做的东西现实中没有合适对应物，不要把 Bar 降级成“高级”“AAA”“漂亮”。

先生成或构造**目标成品应该是什么样**的可检验表示，然后冻结。

例如原创游戏可以先锁：

```text
Hero View
Gameplay State
Crisis State
Character-in-scene State
```

再让真实运行结果逐一与它们比较。

规则：

- Bar 先冻结，候选后判断；
- 候选打不过时不能偷偷生成更容易的新 Bar；
- 只有用户权威真正改变产品目标时才重新绑定；
- Synthetic Visual Bar 只能定义视觉目标，不能证明玩法、交互、运动或性能已成立。

### Hybrid Bar｜混合标杆

不同质量面可以分别使用不同证据：

```text
视觉 → Real / Synthetic visual Bar
运动 → reference clip / runtime Bar
玩法 → scripted playtest
性能 → measured threshold
```

不要揉成一个模糊“总分”。

---

## Gate 与 Bar

**Hard Floor**问“产品成立吗？”：

- 能构建；
- 完整流程可走通；
- 成功、失败、重开存在；
- 性能不越预算；
- 必需内容齐全；
- 没有开放 P0/P1。

**Quality Bar**问“产品够好吗？”：

- 同条件盲 A/B 中，真实画面能否胜过参考？
- 真实运动是否能扛住 reference clip？
- 交互是否比 incumbent 更清楚、更灵敏？
- 最终产物是否达到命名的生产标准？

```bash
# Hard Floor
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . \
  --id FLOW \
  --title "完整流程" \
  --criterion "新玩家可以完成、失败并重新开始规定切片" \
  --owner lead \
  --verifier flow-verifier \
  --machine

# Quality Bar
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . \
  --id BAR \
  --title "真实质量比较" \
  --criterion "等价真实输出证据下，候选达到或击败冻结的 Bar" \
  --owner lead \
  --verifier fresh-critic \
  --bar
```

v0.8+ 的 `VERIFIED` 至少要求一个 required hard-floor gate 与一个 required quality-bar gate。

---

## Critic 必须看真实产物

| 你声称什么 | 至少要看什么 |
|---|---|
| 静态视觉质量 | 截图 / 真实运行帧 |
| 动画 / 镜头 / game feel | clip / runtime / playtest |
| 交互质量 | 实际试玩 / Runtime |
| 场景内资产质量 | 真实场景、相机、比例、灯光、动画中的资产 |
| 性能 | 测量数据 |
| 构建正确 | 真正执行的命令 |
| 产品流程 | 完整真实流程 |
| 比 Bar 更强 | 直接等价比较 |

Critic 每轮只优先返回一个问题：

> **当前最大的一个材料性差距是什么？**

适合盲 A/B 时，隐藏 Builder 历史、自我辩护和 Candidate 身份。位置偏差可能影响结果时，反转顺序或镜像再判。结论冲突就 `INCONCLUSIVE`，不要造一个假的平均分。

---

## 新项目与已有项目

### 新项目

从 Goal 开始。只有真正存在会改变产品结果的歧义时才校准。

游戏目标可以进入 `CALIBRATE`，但它不是访谈配额。如果当前想法已经足够精准，应立即综合并锁定。

### 已有项目

LoopSeed 先恢复可能具有权威性的规划来源：

- `README` / `AGENTS.md`；
- GDD / 产品规格；
- Roadmap / Milestone；
- design / planning / decision records。

已定决定继承，不重新问。

**Context Recovery 与 Creative Dialogue 解耦。** 即使 `--dialogue off`，已有项目发现规划源时仍必须先恢复上下文。

没有规划源则记录 `NONE_FOUND`，继续生产，不制造人工审批 Gate。

---

## Creative Dialogue 的位置

Creative Dialogue 是校准工具，不是生产发动机。

只用来处理会实质改变结果、且无法从当前指令或项目资料解决的歧义。

不要问：

- 仓库里已有答案的事实；
- 可逆的底层实现细节；
- 已经定下来的产品决定。

创意简报锁定后，普通生产判断回到自治循环。

弱截图、测试失败、Critic FAIL 都意味着：

> **Repair。**

不是“要不要继续？”

---

## Fan-out：只拆可独立判断的工作

适合并行：

- 独立资产族；
- 只读调查；
- 独立测试；
- 音频；
- 边界清楚的 UI；
- 性能分析；
- 可以独立 A/B 的视觉或特效面。

强耦合内容保持一个负责人：

- 产品身份；
- 核心循环；
- 共享 Runtime State；
- 架构；
- 全局构图 / 灯光；
- 最终集成。

> **Fan-out 工作，不 Fan-out 对产品的不同理解。**

每轮主要 Fan-out 结束后，先合并局部赢家，再让一个 Fresh Critic 横跨整个产品，找最大跨模块不一致。整体问题没收口前，不开启下一轮大规模 Fan-out。

非简单任务继续使用 `task-graph.json` 的 `HARD_DEPENDENCY` / `SOFT_ADVICE` / `INDEPENDENT` 与 No-idle Scheduler。

---

## 证据与完整性

LoopSeed 用 `verification_binding` 绑定：

```text
真实 Git HEAD
+ 稳定交付产物 SHA-256
+ 当前 binding generation
```

机器 Gate 必须由 Evidence Runner 真执行；写在说明里的命令不算证据。

观察型 PASS 必须指向真实项目内截图、录像、clip 或报告，并记录哈希。

Repair 改变候选后：

1. 旧候选进入历史；
2. 创建新 binding generation；
3. 旧 PASS 失效；
4. 相关 Gate 重新验证。

一张旧截图不能替新 Build 作证。

---

## 状态机与终局

```text
CALIBRATE? → BIND → PLAN → IMPLEMENT → VERIFY
                                      FAIL ↓    ↓ PASS hard + bar
                                         REPAIR → VERIFY → FINALIZE
```

- `VERIFIED`：Hard Floor 与 Bar 都有当前证据，必需工作完成，没有阻塞缺陷；
- `BLOCKED`：存在 Runtime 无法自行解决的精确外部条件，并写明解除条件；
- `ABORTED`：Owner 明确停止。

低质量、测试失败、不确定、第一条路线走不通，都不是 BLOCKED，而是修复、回滚或重规划信号。

连续两轮没有材料性进展，强制根因重规划并换路线。

---

## 最小验证闭环

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py init \
  --root . --goal "<goal>" --dialogue off

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . --id FLOW --title "Flow" --criterion "<可观察硬门槛>" \
  --owner lead --verifier verifier --machine

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . --id BAR --title "Quality Bar" --criterion "<Real / Synthetic / Hybrid 直接比较规则>" \
  --owner lead --verifier fresh-critic --bar

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition \
  --root . --phase PLAN --next "规划最小但有机会赢的路线"
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition \
  --root . --phase IMPLEMENT --next "构建候选"
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition \
  --root . --phase VERIFY --next "冻结并第一手检查真实输出"

head="$(git rev-parse HEAD)"
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py bind \
  --root . --project "my-project" --candidate "$head" --artifact build/output.zip

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py run-evidence \
  --root . --gate FLOW --actor verifier --command "python tools/verify.py" \
  --project "my-project" --candidate "$head" --artifact build/output.zip

# Fresh Critic 尽量亲自运行候选，并记录与声明质量面匹配的 screenshot / clip / report。
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py record \
  --root . --gate BAR --result PASS --actor fresh-critic \
  --summary "候选赢得冻结的等价比较" \
  --artifact captures/bar-verdict.mp4

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py finalize --root .
```

---

## 成本纪律

```text
一个线程足够       → 不 Fan-out
一次真实比较足够   → 不造评审官僚系统
一个 Critic 足够   → 不建评审委员会
机器证据足够       → 不用说明文字代替
```

两条治理原则不变：

> **No new mechanism without demonstrated product effect.**

> **Every new control must replace more uncertainty than complexity it introduces.**

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
