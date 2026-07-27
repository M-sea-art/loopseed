# LOOPSEED One-Shot Production Integrity Patch v0.3.1

## Goal

验证：一次用户意图能否在保持 LOOPSEED 高杠杆 One-Shot 特性的同时，始终服务正确项目、交付正确产物，并达到约定完成阶段。

核心假设：

> 最少语言 + 最大上下文触发 + 正确生产绑定 = 高杠杆 One-Shot 生成。

v0.3.1 保留 v0.2 Expert Activation 与 v0.3 Task Graph、Fan-out、Merge、Critic，只补三个上游语义锁：

- Project Binding：当前任务属于哪个项目。
- Artifact Contract：必须交付什么，不能用什么替代。
- Stage Awareness：目标应达到哪个完成阶段。

这不是新的 Agent 层。三个锁在生产前一次编译，并由所有任务继承。

## Failure Addressed

当错误项目的提示词、审美合同或验收标准被带入当前任务时，后续步骤可能全部局部 PASS，却高效完成了错误目标。Fan-out 只会放大这类上游偏航。

因此：

- 可运行不等于视觉完成。
- 无报错不等于产物正确。
- Blockout 只有在目标本来就是 Blockout 时才能通过。
- 其他项目的合同不得自动继承。

## Pipeline

```text
User Intent
    ↓
Intent Parser
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

## Integrity Lock

每次生产必须生成并冻结：

```text
project_binding_id
artifact_contract_id
stage_target_id
```

Task、Fan-out 输出、Merge 输入和最终 Artifact 必须携带同一组引用。任何引用缺失、冲突或跨项目污染，都在执行或合并前阻断。

权威顺序：

1. 当前明确用户目标
2. 已绑定的项目权威来源
3. Artifact Contract 与 Stage Target
4. Expert / Brand 触发出的可迁移原则
5. Worker 提案

低优先级信息不得改写高优先级合同。

## Production Rules

- 不修改 main。
- 不扩展成复杂 Agent Framework。
- Fan-out 工作，不 Fan-out 人格。
- 只并行边界清晰、合同一致的独立产物。
- 最终由单一执行责任收敛。
- Fast Path 也必须通过三个语义锁。
- 不要求用户逐阶段确认；无冲突时自主执行，有冲突时在生产前失败关闭。
- 验证标准不因速度模式降低。

## Protocol Files

- `project-binding-schema.yaml`
- `artifact-contract-schema.yaml`
- `stage-awareness-policy.yaml`
- `expert-activation-policy.yaml`
- `task-graph-schema.yaml`
- `fanout-policy.yaml`
- `merge-contract.yaml`
- `critic-loop.yaml`
- `brand-trigger-schema.yaml`

## Isolated Benchmarks

- `benchmarks/wuxiang-zen-hall.yaml`
- `benchmarks/xuanmi-sect.yaml`
- `benchmarks/cross-project-contamination.yaml`

两个项目只能使用各自绑定的项目合同。跨项目参考只有在用户明确要求且仅提取可迁移原则时才允许进入当前任务。

## Success Criteria

- 更少用户指令
- 更强项目一致性
- 正确产物类型不被技术样架替代
- 目标阶段与实际证据一致
- Fan-out 后仍保持同一生产合同
- 跨项目污染在执行前被识别
- 更少人工修正
