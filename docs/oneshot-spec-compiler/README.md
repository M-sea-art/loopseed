# LOOPSEED One-Shot Calibration Upgrade v0.4.0

## Goal

验证：一句自然语言项目种子，能否先由系统读取项目、推断规划与技术路线，并在必要时通过一次高杠杆问答完成校准，随后不中断地完成完整生产。

核心假设：

> 最少语言 + 自适应校准 + 最大上下文触发 + 正确生产绑定 = 更有力量的 One-Shot。

v0.4.0 完整保留 v0.3.1 的 Project Binding、Artifact Contract、Stage Awareness，以及已有 Expert Activation、Task Graph、Fan-out、Merge、Critic 与 Verification；只在三重绑定之前增加一个薄的 `One-Shot Calibration` 入口。

它不是新 Agent，不是第四个锁，也不是传统的多轮需求访谈。

## One-Shot Definition

LOOPSEED 中的 One-Shot 定义为：

> 一次经过校准、合同冻结后不中途反复改变方向的完整生产执行。

因此：

- One-Shot 不强制等于一条用户消息。
- 用户最初的一句话仍是项目的语义种子和最高意图锚点。
- 问答只负责消除会改变整个生产结果的关键歧义。
- 用户回答校准问题，即授权后续完整生产。
- 回答后不再询问“是否开始”，不逐阶段要求确认。

## Failure Addressed

直接把一句项目种子送入执行，可能出现两类相反错误：

1. **盲射**：项目、产物、完成阶段或参考角色尚未清楚，系统却立即实施。
2. **问答膨胀**：系统把本可自行推断的技术和产品细节全部推回给用户，One-Shot 退化为传统需求流程。

v0.4.0 的目标不是增加更多交互，而是只暴露少量高杠杆决策面：

- 当前项目与产品结果是什么。
- 核心体验或核心工作是什么。
- 最终交付什么产物。
- 要达到哪个完成阶段。
- 哪项技术路线取舍会改变产品形态或交付目标。
- 参考资料扮演什么角色。
- 哪种替代结果绝对不能通过。
- 用什么证据证明完成。

## Pipeline

```text
Seed Prompt
    ↓
Project Discovery
    ↓
Project Plan + Stack Inference
    ↓
Adaptive Calibration Decision
    ├── Clear → Direct Shot
    └── Material Ambiguity → One-Round Calibrated Shot
                                  ↓
                           User Answer = Authorization
    ↓
Compiled Shot
    ↓
Project Binding
    ↓
Artifact Contract
    ↓
Stage Target
    ↓
Domain Detection
    ↓
Expert Activation
    ↓
Task Graph
    ↓
Fan-out
    ↓
Merge
    ↓
Alignment Critic
    ↓
Repair
    ↓
Verification
    ↓
Artifact
```

## Adaptive Routes

### Direct Shot

当项目身份、产物、阶段、规划范围、技术路线、参考角色和验收证据都可从当前目标与项目证据中可靠推断时：

- 不为了形式而提问。
- 直接编译 Compiled Shot。
- 冻结三重绑定。
- 进入完整生产。

### Calibrated Shot

只有当某个未决选择会实质改变项目、产品形态、核心体验、产物、阶段、技术路线或验收时：

- 先展示已推断状态。
- 先给出推荐项目规划与推荐技术栈。
- 最多集中提出一轮、五个高杠杆问题。
- 每题提供互斥选项、推荐项和关键后果。
- 不询问仓库中已经存在的事实。
- 不询问可逆的底层工程细节。
- 不把用户拖入库、框架或样式参数的无意义选择。

如果用户回答“全部按推荐”，即视为完成校准并授权执行。

## Planning and Stack Responsibility

项目规划与技术栈首先是编译器责任，而不是用户填表责任。

系统必须：

- 从当前项目、目标产物和目标阶段推断一个有边界的单次生产计划。
- 优先使用能够满足合同的项目原生技术栈。
- 主动推荐技术路线并解释其项目适配、产物适配和阶段适配。
- 只在技术选择会改变产品形态、交付目标或不可逆成本时要求用户裁决。
- 保留可逆、低层、实现型决策给执行者自主完成。
- 不得为了实现方便而降低产品野心、替换产物或下调阶段。

技术路线属于 Artifact Contract 的实施策略，不构成第四个完整性锁。

## Seed Intent Preservation

最初项目种子不可被校准过程改写成更容易实现的另一种产品。

允许：

- 消除歧义。
- 确定优先级。
- 在不改变产品身份的前提下限定本轮范围。
- 加强验收与证据。
- 选择更适合目标的技术路线。

禁止：

- 把游戏替换成静态 UI、场景漫游或几何 Blockout。
- 把视觉完成改写成功能可运行。
- 把完整核心循环改写成单个机制样架。
- 让参考项目覆盖当前项目身份和合同。
- 以工程便利性为理由降低用户真实目标。

## Compiled Shot

校准结果被压缩为一份简短、可执行的 `Compiled Shot`，至少包含：

- seed intent
- product outcome
- core experience or job
- bounded scope
- Project Binding
- Artifact Contract
- Stage Target
- implementation strategy
- reference roles
- non-goals
- required evidence

`Compiled Shot` 是人类可读的执行简报，不是第四个锁。

生产仍然只冻结：

```text
project_binding_id
artifact_contract_id
stage_target_id
```

Task、Fan-out 输出、Merge 输入和最终 Artifact 必须携带同一组引用。任何引用缺失、冲突、跨项目污染、种子意图漂移或未经授权的产物替代，都必须在执行或合并前阻断。

## Authority Order

1. 当前明确用户目标与校准回答
2. 已绑定的项目权威来源
3. 冻结的 Artifact Contract 与 Stage Target
4. 选定的 implementation strategy
5. Expert / Brand 触发出的可迁移原则
6. Worker 提案

低优先级信息不得改写高优先级合同。

## Production Rules

- 不修改 main。
- 不扩展成复杂 Agent Framework。
- 校准最多一轮、五个问题。
- 无重大歧义时跳过问答。
- 校准期间不写入生产文件。
- 推荐之后再询问，不把架构责任推回给用户。
- 用户回答后直接冻结并执行，不要求第二次确认。
- Fan-out 工作，不 Fan-out 人格、项目身份或生产合同。
- 只并行边界清晰、合同一致的独立产物。
- 最终由单一执行责任收敛。
- Fast Path 与 Direct Shot 仍必须通过三个语义锁。
- 验证标准不因速度模式降低。
- Critic 必须检查种子意图、项目、产物、实施策略、阶段和证据是否一致。

## Protocol Files

- `calibration-policy.yaml`
- `project-binding-schema.yaml`
- `artifact-contract-schema.yaml`
- `stage-awareness-policy.yaml`
- `expert-activation-policy.yaml`
- `task-graph-schema.yaml`
- `fanout-policy.yaml`
- `merge-contract.yaml`
- `critic-loop.yaml`
- `brand-trigger-schema.yaml`

## Benchmarks

- `benchmarks/oneshot-calibration.yaml`
- `benchmarks/wuxiang-zen-hall.yaml`
- `benchmarks/xuanmi-sect.yaml`
- `benchmarks/cross-project-contamination.yaml`

无相禅堂与玄秘门派仍只能使用各自绑定的项目合同。跨项目参考只有在用户明确要求且仅提取可迁移原则时才允许进入当前任务。

新增校准 benchmark 必须同时验证：

- 清楚目标不被强制提问。
- 高影响歧义最多经过一轮问答。
- 系统先提出规划与技术栈建议，再让用户裁决战略取舍。
- 初始种子不会被简化成更容易实现的替代产品。
- 问答结果只编译进现有三重绑定。
- 用户回答后不再要求第二次确认。

## Success Criteria

- 用户仍可从一句自然语言项目种子开始。
- 更少盲射和项目返工。
- 更少低价值问题。
- 技术栈与真实项目、产物和目标阶段一致。
- 原始意图在校准后更清晰、更有力量，而不是被削弱。
- 正确产物类型不被技术样架替代。
- Fan-out 后仍保持同一生产合同。
- 完成声明有真实、阶段对应的证据。
- 整个流程仍然保持最少语言、最大杠杆和一次生产完成。
