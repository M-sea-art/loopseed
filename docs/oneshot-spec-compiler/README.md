# LOOPSEED One-Shot Spec Compiler v0.1 Experiment

## Goal

验证：是否可以通过一次用户意图输入，自动编译出接近专家团队需求文档质量的生成任务。

核心假设：

> 最少语言 + 最大上下文触发 = 高杠杆 One-Shot 生成。

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
Brand Trigger Expansion
    ↓
Generation Contract
    ↓
Self Critic
    ↓
Artifact
```

## Experiment Rule

- 不修改 main。
- 不追求功能堆叠。
- 只验证一次输入是否获得更高质量输出。
- 使用真实项目作为 benchmark。

## Benchmark

1. 无相禅堂直播互动游戏
2. 玄秘门派模拟器
3. 内容创作流程

## Success Criteria

- 更少用户指令
- 更强领域一致性
- 更接近成品级结果
- 更少人工修正
