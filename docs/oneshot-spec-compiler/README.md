# LOOPSEED One-Shot Spec Compiler v0.3 Experiment

## Goal

验证：是否可以通过一次用户意图输入，自动编译并组织接近专家团队生产流程的执行任务。

核心假设：

> 最少语言 + 最大上下文触发 + 生产路径展开 = 高杠杆 One-Shot 生成。

v0.3 在 v0.2 Expert Activation 基础上增加生产组织能力：

- Fan-out：拆分可并行生产轨道，而不是增加无关角色。
- Merge：由主执行流程统一收敛产物。
- Critic Loop：发现最大可见缺陷后进行定向修复。

## Pipeline

```
User Intent
    ↓
Intent Parser
    ↓
Domain Detection
    ↓
Expert Registry Injection
    ↓
Task Graph Generation
    ↓
Fan-out Execution
    ↓
Merge Contract
    ↓
Self Critic
    ↓
Repair
    ↓
Artifact
```

## Production Rule

- 不修改 main。
- 不追求 Agent 数量。
- Fan-out 工作，不 Fan-out 人格。
- 只拆分具有明确边界的独立产物。
- 最终由单一执行责任收敛。
- 验证标准不因 Fast Path 降低。

## Experiment Rule

- 不修改 main。
- 不追求功能堆叠。
- 使用真实项目作为 benchmark。
- 优先验证交付速度、产物质量和人工介入减少。

## Benchmark

1. 无相禅堂直播互动游戏
2. 玄秘门派模拟器
3. 内容创作流程

## Success Criteria

- 更少用户指令
- 更强领域一致性
- 更快形成可交付产物
- 更接近成品级结果
- 更少人工修正
- 能在并行后保持统一产品方向
