---
loopseed_version: "0.7.1"
last_updated: "2026-08-09"
update_policy: "required-on-every-version-upgrade"
---

# LOOPSEED 生产使用技巧

> 最小指令，最大有效自治；默认走最低成本路径，只有真实产品收益或真实风险证明值得时才加重流程。

这是 LOOPSEED 当前生产入口的简明真相页。版本、运行模式、关键命令或证据边界改变时，本页必须同步更新；CI 会检查这里声明的版本与 `.codex-plugin/plugin.json` 一致。

## 1. 先选最轻的模式

### 标准 LoopSeed：明确的小任务

```text
$loopseed <目标>
```

适合修一个 bug、补一个小功能、修改一个页面或脚本、增加相关测试、制作一个很小的游戏机制。

默认闭环：

```text
探索 → 行动 → 观察 → 验证 → 调整
```

默认一个主线程、一个写入者、一个集成路径。不要为了显得“智能”而默认创建子智能体、Worktree、Critic 或长循环。

### One‑Shotted：完整切片或一次授权生产

```text
$loopseed one-shotted <一句自然语言目标>
```

适合从零完成一个小游戏、可交付垂直切片、已有仓库中的完整功能，或需要一次授权后自主规划、实现、验证、修复和终局判断的任务。

“One‑Shotted”表示一次正式生产授权，不表示一次模型回复。游戏种子默认可先进入创意校准；简报锁定后不应反复要求用户发送“继续”。

## 2. 游戏项目怎么用

不需要先写完整 GDD。给出真正想要的体验种子即可，例如：

```text
$loopseed one-shotted 做一个武侠门派经营垂直切片。弟子有自己的欲望和关系，玩家通过资源、规则和关键决定间接影响门派。先把会改变产品结果的关键选择校准清楚，再一次授权完成可试玩、可失败、可重开并有真实视觉与运行证据的切片。
```

创意对话只问会改变产品结果的问题；方向清楚就锁定，不为凑轮次继续盘问。必须保留用户已经接受的决定，不能偷偷把游戏降级为静态场景、普通 Dashboard、几何 Blockout 或“能跑就算完成”的原型。

## 3. 什么时候才开 Fan‑out / Critic

只在满足下面条件时升级运行拓扑：

- 任务真实独立，能够分别验收；
- 写入范围可以隔离；
- 并行确实比协调成本更划算；
- 最终仍有一个 Lead 收敛为一个产品。

适合并行：独立资产族、只读调查、独立测试、音频、边界清晰的 UI、性能分析。

不要并行不同的“产品理解”：产品身份、核心循环、共享状态、技术架构、全局灯光/构图、整体集成和最终放行应保持单一权威。

Critic 不是默认仪式。只有当结果存在重要但机器测试无法判定的质量面时才启用，例如整体视觉、第一次玩家理解、交互反馈或成品感。

## 4. v0.7.1 的真实性边界

v0.7.1 增加的是 **候选与交付产物完整性桥（Candidate & Artifact Integrity Bridge）**。

它会把：

```text
真实 Git HEAD
+ 稳定交付产物 SHA‑256
+ 真实执行的 verifier command
+ exit code / timeout / 有界输出
+ tracked worktree / untracked content 检查
```

绑定到当前验证代，并在修复改变候选后使旧 PASS 失效。人工或视觉 PASS 必须引用真实存在并被哈希的项目内证据文件。

它**不是完整的 hermetic / supply-chain attestation**。`.gitignore` 中的可变源码、环境状态、外部路径或未显式绑定的 verifier 输入并不会自动获得同等级证明。因此 verifier 不应依赖这些可变输入；若项目必须依赖它们，应把它们提交、复制进项目并固定，或明确把该限制记录为验证边界。

## 5. 一个最小的 One‑Shotted 验证闭环

```text
CALIBRATE（游戏可选/默认）
  ↓
BIND → PLAN → IMPLEMENT → VERIFY
                       失败 ↓    ↓ 通过
                          REPAIR → VERIFY → FINALIZE
```

生产完成前至少满足：

- 大规模实现前声明可观察 Gate；
- 实现者不能审核自己的 Gate；
- required task 全部 `SUCCEEDED`；
- optional task 也必须显式收口；
- 机器 Gate 由 `run-evidence` 真执行；
- 人工/视觉 Gate 有真实哈希产物；
- 修复后重新绑定、重新验证；
- 没有开放 P0/P1；
- final report 与当前 run、Gate、证据、任务和 binding 一致。

常用命令：

```bash
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py init --root . --goal "<goal>"
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate --root . --id FLOW --title "Flow" --criterion "<observable criterion>" --owner lead --verifier verifier --machine
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition --root . --phase PLAN --next "Plan bounded work"
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition --root . --phase IMPLEMENT --next "Build and commit candidate"
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py transition --root . --phase VERIFY --next "Freeze candidate"
head="$(git rev-parse HEAD)"
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py bind --root . --project "my-project" --candidate "$head" --artifact build/output.zip
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py run-evidence --root . --gate FLOW --actor verifier --command "python tools/verify.py" --project "my-project" --candidate "$head" --artifact build/output.zip
python <PLUGIN_ROOT>/skills/loopseed/scripts/one_shotted.py finalize --root .
```

## 6. 成本纪律

LOOPSEED 的默认顺序是：

```text
单线程足够 → 不并行
机器证据足够 → 不加人工 Critic
一个 Critic 足够 → 不建评审委员会
一个真实 A/B 足够回答问题 → 不先升级 Runtime
```

两个核心治理规则：

> **No new mechanism without demonstrated product effect.**
>
> 没有证明能让结果更好的机制，不进入核心。

> **Every new control must replace more uncertainty than complexity it introduces.**
>
> 新控制消除的不确定性，必须大于它增加的复杂度。

## 7. 当前生产真相

- `main`：v0.7.0，当前已发布稳定基线。
- `agent/v0.7.1-integrity-bridge`：v0.7.1 候选，补候选/产物真实性与终局交叉验证；合并前必须通过 Linux 与 Windows 的最小真实闭环。
- 旧 `experiment/*` 与旧 Draft PR：只作为历史实验、证据或后续产品效果 A/B 的来源，不应被当成当前生产入口。

## 8. 下一步不是堆机制

v0.7.1 之后，优先做等预算产品效果实验：一次只测试一个候选机制，例如动态专家、创意对话或 Reality Gate。只有结果质量、完成率、成本或时间出现可复现收益，候选机制才有资格进入核心。

跨项目长期记忆与更多默认专家暂不进入 Runtime，避免经验污染和协调复杂度先于产品收益增长。
