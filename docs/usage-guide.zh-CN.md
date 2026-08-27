---
loopseed_version: "0.8.0"
last_updated: "2026-08-27"
update_policy: "required-on-every-version-upgrade"
---

# LOOPSEED 生产使用技巧

> **Gate 是地板，Bar 是天花板。**
>
> 用最少语言把目标与真实质量标杆钉住，让 Agent 自己决定生产路线；上下文、证据、并发与完整性治理退到后台，只在它们能减少真实不确定性时介入。

这是 LOOPSEED v0.8 的生产真相页。版本、运行模式、关键命令或证据边界改变时，本页必须同步更新；CI 会检查这里声明的版本与 `.codex-plugin/plugin.json` 一致。

## 1. v0.8 的最短心智模型

```text
GOAL：要做什么
  ↓
BAR：什么叫真的好
  ↓
Agent 自己拆解与选择路线
  ↓
真实产物 / 真实运行
  ↓
Fresh Critic 独立检查
  ↓
Blind A/B（适合时）
  ↓
只找一个最大差距
  ↓
修复 → 再观察 → 再比较
  ↓
赢家冻结，输家回滚
```

Runtime Shell 在后台负责：项目上下文恢复、Artifact/Commit Binding、任务所有权、No-idle 调度、哈希证据、独立验证、修复重绑和可恢复状态。

**Shell 不拥有产品质量裁决权。Bar 才拥有。**

## 2. 先选最轻的入口

### 标准 LoopSeed：小而明确的任务

```text
$loopseed <目标>
```

适合一个 bug、一个小功能、一个局部页面、一个脚本或一个小机制。

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

## 3. 新项目：默认先 Goal + Bar，不先采访

如果目标已经清楚，推荐直接关闭创意访谈：

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py init \
  --root . \
  --goal "<goal>" \
  --dialogue off
```

然后声明**最少的硬门槛**与**一个真正可检验的质量 Bar**。

硬门槛示例：

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . \
  --id BUILD \
  --title "Runnable build" \
  --criterion "目标构建可以启动并完整走通要求流程" \
  --owner lead \
  --verifier verifier \
  --machine
```

质量 Bar 示例：

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . \
  --id BAR \
  --title "Inspectable quality bar" \
  --criterion "在等价截图/录像/运行条件下，候选达到或击败指定参考或 incumbent，同时不损失产品核心身份" \
  --owner lead \
  --verifier fresh-critic \
  --bar
```

v0.8 不允许只有 BUILD/FLOW 等工程 Gate 全绿就写 `VERIFIED`。

## 4. 什么是好的 Bar

优先选择 Agent **真的能够检查和比较**的东西：

- 游戏/UI 视觉：真实参考截图，同视角、同分辨率、同状态比较；
- 游戏体验：固定输入录像、首分钟理解目标、完整成功/失败/重开流；
- 3D 资产：参考渲染 + 目标引擎真实导入/运行；
- 软件：标准、兼容性测试、性能 benchmark、已知稳定 incumbent；
- 写作/报告：用户提供的刊物/文风参考 + 事实与结构 Gate。

没有单一参考时，使用多个正交证据通道，不把它们揉成一个模糊总分。

```text
工程 PASS ≠ 产品 PASS
视觉 PASS ≠ 行为 PASS
漂亮截图 ≠ 可玩
能运行 ≠ 成品
```

## 5. Critic 怎么工作

Fresh Critic 要看**真实产物**，不是 Builder 的解释。

适合时匿名为 X/Y：

1. 等价条件采集；
2. 隐藏新旧身份与 Builder 自辩；
3. 先判赢家，再解释；
4. 输出一个最大的剩余差距；
5. 需要时反转顺序再判；
6. 两次明显冲突就记 `INCONCLUSIVE`，不能平均成假精确分数。

推荐输出：

```text
VERDICT: PASS | FAIL | X_WINS | Y_WINS | INCONCLUSIVE
CONFIDENCE: low | medium | high

EVIDENCE:
- <真实观察>

SINGLE BIGGEST GAP:
- <最高价值的一个差距>

BOUNDED REPAIR:
- <一个因果清晰的修复单元>

DO NOT TOUCH:
- <已经通过或不能丢失的部分>
```

## 6. Ratchet：新版不自动赢

每轮只做一个清晰判断：

```text
challenger 赢 → 晋级并冻结
challenger 输 → 回滚
证据冲突 → 保留 incumbent，INCONCLUSIVE
硬门槛失败 → FAIL
连续两轮同类修复无进展 → 根因重规划 / STRUCTURAL RESET
```

不要因为“这是新版”“代码更多”“花了更多时间”就给它加分。

## 7. 已有项目：先恢复已定意图，再继续射击

已有项目不能为了重新获得创作自由而忘掉旧决策。

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

恢复的目的，是**少问用户问题**，不是多造一个流程。

## 8. Creative Dialogue 什么时候才开

只有一个条件：

> 存在无法从当前指令或项目权威资料解决、而且会实质改变产品结果的歧义。

这时才使用 `--dialogue on`。

不要问：可逆的技术细节、仓库里已有答案、仅仅因为还没凑满对话轮数的问题。

方向一旦清楚就锁定，马上回到 Goal + Bar 生产。

## 9. Fan-out 什么时候才值得

并行不是 Gauntlet 的灵魂。

只有在下面条件成立时才 Fan-out：

- 工作真实独立；
- 写入所有权可隔离；
- 能分别验收；
- 选择价值高于协调成本。

产品身份、核心循环、共享状态、架构、全局构图/灯光和最终集成保持一个 Lead。

一个强 Builder + 一个 Fresh Critic，完全可以是有效的 Gauntlet。

## 10. v0.8 的 One-Shotted 终局

```text
CALIBRATE? → BIND → PLAN → IMPLEMENT → VERIFY
                                      ↓ FAIL
                                    REPAIR
                                      ↓
                                    VERIFY
                                      ↓ hard + bar PASS
                                   FINALIZE
```

`CALIBRATE` 是可选的。

`VERIFIED` 至少需要：

- 至少一个 required `hard` gate；
- 至少一个 required `bar` gate；
- 所有 required gate 当前绑定证据均 PASS；
- 实现者没有审核自己的 Gate；
- required task 全部 `SUCCEEDED`；
- optional task 显式收口；
- 机器 Gate 真实由 `run-evidence` 执行；
- 视觉/体验 Gate 引用真实哈希产物；
- 修复后重新绑定、重新验证；
- 无开放 P0/P1；
- final report 与当前 run / Gate / evidence / task / binding 一致。

### 一个完整最小闭环

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py init --root . --goal "<goal>" --dialogue off

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate --root . --id FLOW --title "Flow" --criterion "<observable hard-floor criterion>" --owner lead --verifier verifier --machine

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate --root . --id BAR --title "Quality bar" --criterion "<inspectable reference/incumbent comparison rule>" --owner lead --verifier fresh-critic --bar

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition --root . --phase PLAN --next "Choose the smallest route that can beat the bar"
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition --root . --phase IMPLEMENT --next "Build and commit candidate"
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition --root . --phase VERIFY --next "Freeze candidate and inspect real output"

head="$(git rev-parse HEAD)"
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py bind --root . --project "my-project" --candidate "$head" --artifact build/output.zip

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py run-evidence --root . --gate FLOW --actor verifier --command "python tools/verify.py" --project "my-project" --candidate "$head" --artifact build/output.zip

# BAR 通常由 fresh critic 根据真实截图/录像/运行证据，用 record 写入独立 PASS/FAIL。

python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py finalize --root .
```

## 11. 诚实停止，不是假装无限循环

Bar 不意味着无限烧预算。

合法结果包括：

- `VERIFIED`：硬地板和 Bar 都有直接证据证明通过；
- `INCONCLUSIVE`：证据不能可靠判定；
- `ROLLBACK`：challenger 输，保留 incumbent；
- `STRUCTURAL_RESET`：局部修补已不合理，换路线；
- `BLOCKED`：存在精确、不可替代的外部阻塞；
- `ABORTED`：用户明确停止。

预算耗尽、Critic 仍然发现明显 Bar 差距、证据缺失，都不能伪装成 PASS。

## 12. 成本纪律

```text
单线程够 → 不并行
机器证据够 → 不加额外 Critic
一个 Critic 够 → 不建委员会
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

## 13. 当前版本真相

- `main`：v0.7.1 integrity bridge 稳定基线。
- `agent/v0.7.2-context-harvest`：恢复已有项目规划与创意共导演进线。
- `agent/v0.8.0-gauntlet-kernel`：把 Gauntlet 恢复为 Seed Kernel，并将 Context / Evidence / Integrity / Scheduler 明确降为 Runtime Shell；`VERIFIED` 新增强制 Bar Gate。

v0.8 的目标不是再增加更多机制，而是**重新排列权力关系**：

> Runtime 负责不失忆、不跑偏、不造假、不互踩。
>
> Gauntlet 负责让成品不断逼近并击败真实质量标杆。
