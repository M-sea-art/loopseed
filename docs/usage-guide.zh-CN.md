---
loopseed_version: "0.8.1"
last_updated: "2026-08-28"
update_policy: "required-on-every-version-upgrade"
---

# LOOPSEED 生产使用技巧

> **Gate 是地板，Bar 是天花板。**
>
> **游戏要在运动中判，Critic 要亲自看，资产要放进产品里判，并行之后要重新看整个产品。**

这是 LOOPSEED v0.8.1 的生产真相页。版本、运行模式、关键命令或证据边界改变时，本页必须同步更新；CI 会检查这里声明的版本与 `.codex-plugin/plugin.json` 一致。

## 1. 最短心智模型

```text
GOAL：要做什么
  ↓
BAR：什么叫真的好
  ↓
Agent 自己拆解与选择路线
  ↓
真实产物 / 真实运行
  ↓
Fresh Critic 第一手检查
  ↓
Blind / equivalent A-B（适合时）
  ↓
只找一个最大差距
  ↓
修复 → 再运行 → 再比较
  ↓
赢家冻结，输家回滚
```

Runtime Shell 在后台负责：项目上下文恢复、Artifact/Commit Binding、任务所有权、No-idle 调度、哈希证据、独立验证、修复重绑和可恢复状态。

**Shell 不拥有产品质量裁决权。Bar 才拥有。**

## 2. v0.8.1 新增的四条生产硬规则

### 2.1 游戏在运动中判

如果质量声明涉及：

- 动画；
- 镜头运动；
- 战斗阅读性；
- 尺度感；
- 粒子与尘土；
- 输入反馈；
- 节奏；
- game feel；

那么一张漂亮截图不能证明 PASS。

```text
Still win ≠ Motion win
```

必须用录像、实时运行、试玩或其他能够观察运动的证据。

### 2.2 Critic 必须尽量第一手观察

能力允许时，Fresh Critic 自己：

```text
启动真实 Build
→ 玩 / 操作 / 浏览
→ 自己截图和录片段
→ 自己记录测量
→ 再和 Bar 比
```

Critic 不应把 Builder 挑选的几张“最好看截图”和 Builder 的自我解释当主要证据。

如果 Critic 无法访问 Runtime，必须明确声明限制；此时不能从静态图推断 motion、interaction 或 game feel 已通过。

### 2.3 生成资产必须放进产品里判

角色、模型、精灵、特效、动画、材质的独立 Render 可以做 sanity check，但不能单独获得最终的产品质量 PASS。

只要这些因素会影响结果，就必须在真实场景中检查：

```text
真实相机
+ 真实比例
+ 真实灯光
+ 真实 UI
+ 真实动画
+ 真实运行状态
```

**Asset Quality 最终要变成 Asset-in-Product Quality。**

### 2.4 每轮主要 Fan-out 后重新整体化

局部都变好，不代表整个产品变好。

每次主要并行改善波次结束后：

```text
合并所有局部赢家
  ↓
Fresh Whole-Product Critic
  ↓
找一个最大的跨模块不一致
  ↓
先修整体一致性
  ↓
再开下一轮大规模 Fan-out
```

局部 Agent 可以分别提高地形、角色、FX、UI，但最终必须重新判断它们是不是还属于**同一个游戏**。

## 3. 先选最轻的入口

### 标准 LoopSeed：小而明确的任务

```text
$loopseed <目标>
```

默认：

```text
探索 → 行动 → 真实观察 → 批评 → 调整
```

能单线程闭环就不 Fan-out；机器测试足够就不建评审委员会。

### One-Shotted：一次授权完成完整生产

```text
$loopseed one-shotted <一句自然语言目标>
```

适合小游戏、垂直切片、完整功能、视觉重构或需要持续自主修复的生产任务。

“One-Shotted”指一次生产授权，不指一次模型回复。

## 4. 新项目：默认先 Goal + Bar，不先采访

如果目标已经清楚，推荐直接关闭创意访谈：

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py init \
  --root . \
  --goal "<goal>" \
  --dialogue off
```

然后声明最少的硬门槛与一个真正可检验的质量 Bar。

```bash
# Hard Floor
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . \
  --id FLOW \
  --title "Complete flow" \
  --criterion "目标构建可以启动并完整走通要求流程" \
  --owner lead \
  --verifier verifier \
  --machine

# Quality Bar
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . \
  --id BAR \
  --title "Inspectable quality bar" \
  --criterion "在等价真实运行证据下，候选达到或击败锁定 Bar，同时不损失产品核心身份" \
  --owner lead \
  --verifier fresh-critic \
  --bar
```

v0.8+ 不允许只有 BUILD/FLOW 等工程 Gate 全绿就写 `VERIFIED`。

## 5. Bar 分三种

### Real Bar｜现实标杆

优先使用现实中可直接比较的：

- 游戏或产品；
- reference frames / clips；
- incumbent build；
- benchmark；
- 可测目标。

### Synthetic Bar｜生成标杆

如果你要做的东西没有有意义的现实世界对应物，不要把 Bar 降级成“高级、AAA、漂亮”。

可以先生成或构造**目标成品应该呈现的可检查表示**，然后冻结为 Synthetic Bar。

例如原创游戏视觉：

```text
用户意图
  ↓
生成目标 Hero View / Gameplay State / Crisis State
  ↓
选定并冻结目标图
  ↓
真实游戏运行截图 / 录像
  ↕
Synthetic Bar
```

关键规则：

- Synthetic Bar 必须先冻结，再用来判断对应候选；
- 不能因为候选打不过就偷偷重生成更容易的 Bar；
- 用户明确改变产品方向时，才重新绑定 Bar；
- 生成视觉 Bar 只能定义视觉目标，不能证明玩法、交互或性能已经成立。

### Hybrid Bar｜混合标杆

不同质量面没有同一个参考时，明确分开：

```text
视觉 → Synthetic / Real visual Bar
运动 → reference clip / runtime Bar
玩法 → scripted playtest Bar
性能 → measured threshold
```

不要揉成一个模糊“总分”。

## 6. 什么是好的游戏 Bar

优先选择 Agent **真的能够检查和比较**的东西：

- 静态视觉：同视角、同分辨率、同状态截图；
- 动态视觉：等价镜头与状态下的 clips；
- 游戏体验：固定输入录像、完整成功/失败/重开流；
- 3D/角色资产：参考 + 目标引擎真实导入 + 场景内比例/灯光/动画检查；
- 性能：FPS、帧时间、内存、加载时间等测量；
- 没有现实补充的原创视觉：冻结的 Synthetic Bar。

```text
工程 PASS ≠ 产品 PASS
视觉 PASS ≠ 行为 PASS
Still PASS ≠ Motion PASS
孤立资产 PASS ≠ 场景内 PASS
能运行 ≠ 成品
```

## 7. Critic 怎么工作

Fresh Critic 看真实产物，不看 Builder 的“我做得很好”。

理想路径：

```text
Critic 启动真实 Build
  ↓
自己玩 / 看 / 操作
  ↓
自己采集 Screenshot + Clip + Measurement
  ↓
和锁定 Bar 做等价比较
  ↓
适合时匿名 X/Y
  ↓
先判赢家，再解释
  ↓
只输出当前最大的一个剩余差距
```

推荐输出：

```text
VERDICT: PASS | FAIL | X_WINS | Y_WINS | INCONCLUSIVE
CONFIDENCE: low | medium | high

EVIDENCE:
- <第一手真实观察 / frame / clip / measurement>

SINGLE BIGGEST GAP:
- <最高价值的一个差距>

BOUNDED REPAIR:
- <一个因果清晰的修复单元>

DO NOT TOUCH:
- <已经通过或不能丢失的部分>
```

适合时反转顺序再判；两次明显冲突就记 `INCONCLUSIVE`，不能平均成假精确分数。

## 8. Ratchet：新版不自动赢

```text
challenger 赢 → 晋级并冻结
challenger 输 → 回滚
证据冲突 → 保留 incumbent，INCONCLUSIVE
硬门槛失败 → FAIL
连续两轮同类修复无进展 → 根因重规划 / STRUCTURAL RESET
```

不要因为“这是新版”“代码更多”“花了更多时间”就给它加分。

## 9. 已有项目：先恢复已定意图

至少检查：

- README / AGENTS.md；
- docs / design / planning / product / spec；
- roadmap / GDD / brief / milestone / decision record；
- 用户最近已明确接受的决定；
- 当前运行产物作为状态证据。

恢复：

```text
哪些决定已经定了
哪些仍然真的开放
哪些资料冲突或过时
当前项目身份是什么
```

恢复的目的是**少问用户问题**，不是多造一个流程。

Context Recovery 与 Creative Dialogue 解耦。即使 `--dialogue off`，已有项目发现规划源时仍先恢复上下文。

## 10. Creative Dialogue 什么时候才开

只有一个条件：

> 存在无法从当前指令或项目权威资料解决、而且会实质改变产品结果的歧义。

这时才使用 `--dialogue on`。

不要问可逆技术细节、仓库已有答案、仅仅因为还没凑满对话轮数的问题。

## 11. Fan-out 什么时候才值得

只有可**独立改进并独立判断**的工作才值得拆出去。

适合：

- 独立资产族；
- 只读调查；
- 独立测试；
- 音频；
- 边界清楚的 UI；
- 性能分析；
- 可独立 A/B 的视觉或特效面。

产品身份、核心循环、共享状态、架构、全局构图/灯光和最终集成保持一个 Lead。

主要 Fan-out wave 结束后必须重新整体化：

> **一个 Fresh Critic 横跨整个产品，先修最大的跨模块不一致，再继续下一波。**

## 12. v0.8.1 的 One-Shotted 终局

```text
CALIBRATE? → BIND → PLAN → IMPLEMENT → VERIFY
                                      ↓ FAIL
                                    REPAIR
                                      ↓
                                    VERIFY
                                      ↓ hard + bar PASS
                                   FINALIZE
```

`VERIFIED` 至少需要：

- 至少一个 required `hard` gate；
- 至少一个 required `bar` gate；
- 所有 required gate 当前绑定证据均 PASS；
- motion claim 在适用时有 motion evidence；
- integrated asset quality 在适用时有 in-product evidence；
- 实现者没有审核自己的 Gate；
- required task 全部 `SUCCEEDED`；
- optional task 显式收口；
- 机器 Gate 真实由 `run-evidence` 执行；
- 视觉/体验 Gate 引用真实哈希产物；
- 修复后重新绑定、重新验证；
- 无开放 P0/P1；
- final report 与当前 run / Gate / evidence / task / binding 一致。

## 13. 诚实停止，不是假装无限循环

Bar 不意味着无限烧预算。

合法结果包括：

- `VERIFIED`：硬地板和 Bar 都有直接证据证明通过；
- `INCONCLUSIVE`：证据不能可靠判定；
- `ROLLBACK`：challenger 输，保留 incumbent；
- `STRUCTURAL_RESET`：局部修补已不合理，换路线；
- `BLOCKED`：存在精确、不可替代的外部阻塞；
- `ABORTED`：用户明确停止。

预算耗尽、Critic 仍然发现明显 Bar 差距、证据缺失，都不能伪装成 PASS。

## 14. 成本纪律

```text
单线程够 → 不并行
一个可检验 Bar 够 → 不造评估委员会
一个 Critic 够 → 不建多层审批
一次可靠 A/B 能回答 → 不先升级 Runtime
治理层没有减少真实不确定性 → 不让它进入主注意力
```

继续保留两条治理原则：

> **No new mechanism without demonstrated product effect.**
>
> 没有证明能让结果更好的机制，不进入核心。

> **Every new control must replace more uncertainty than complexity it introduces.**
>
> 新控制消除的不确定性，必须大于它增加的复杂度。

## 15. 当前版本真相

- `main`：v0.8.0 Gauntlet Kernel 已发布基线。
- `agent/v0.8.1-runtime-observation`：本轮候选，补第一手 Runtime Critic、Motion Evidence、Asset-in-Product、Synthetic Bar 与 Fan-out 后 Whole-Product Critic。

v0.8.1 不改变 v0.8 的权力结构，而是把“比较”进一步变成**真正观察用户最后看到、听到、玩到的东西**：

> Runtime 负责不失忆、不跑偏、不造假、不互踩。
>
> Gauntlet 负责让真实成品不断逼近并击败可检验质量标杆。
