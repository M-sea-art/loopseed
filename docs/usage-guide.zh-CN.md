---
loopseed_version: "0.3.1-c1.1"
last_updated: "2026-07-31"
update_policy: "required-on-every-version-upgrade"
---

# LOOPSEED 生产使用技巧

> 最小指令，最大有效自治；默认走最低成本路径，只有真实证据证明值得时才加重流程。

本文是 LOOPSEED 的长期使用指南。每次版本升级、运行模式变化、命令变化或生产协议变化，都必须同步更新本文；仓库 CI 会检查本文声明的版本是否与 `.codex-plugin/plugin.json` 一致。

## 1. 先选最轻的模式

### 标准模式：小任务与明确修改

```text
$loopseed <目标>
```

适合：

- 修复一个明确 bug；
- 增加一个小功能；
- 修改一个页面、接口或脚本；
- 为现有功能补测试；
- 制作一个很小的游戏机制。

标准模式使用最低成本闭环：

```text
探索 → 行动 → 观察 → 验证 → 调整
```

默认一个 Lead、一个写入者、一个集成路径。不要为了显得“智能”而默认创建子代理、Worktree 或长循环。

示例：

```text
$loopseed 修复当前登录回调偶尔重复提交的问题，保持现有认证流程不变，运行相关测试并报告真实结果。
```

```text
$loopseed 在当前游戏中加入暂停和重开，保持已有移动、碰撞和计分逻辑不变，实际运行验证。
```

### One-Shotted：完整切片与一次授权生产

```text
$loopseed one-shotted <一句自然语言目标>
```

或：

```text
/goal $loopseed one-shotted <一句自然语言目标>
```

适合：

- 从零制作一个完整小游戏；
- 完成一个可交付的产品垂直切片；
- 在已有仓库中交付一个完整功能；
- 希望一次授权后由系统自主规划、实现、验证、修复并终局判断；
- 任务可能进入真实 `BLOCKED`，之后需要凭新证据恢复。

“One-Shotted”表示一次人类授权，不表示一次模型回复。系统内部可以多轮使用工具、运行测试、独立验收和修复，但不要求用户不断发送“继续”。

## 2. 当前版本怎么选

| 使用目的 | 推荐分支 / 版本 | 说明 |
|---|---|---|
| 日常稳定生产 | `main` / v0.3.0 | 当前正式稳定版 |
| 重要现有仓库、严格绑定与机器证据 | `experiment/c1.1-binding-integrity-repair-2026-07-30` | 实验候选，尚未晋升 `main` |
| 参考最新生产方法 | `experiment/oneshot-production-upgrade` | Calibration、Artifact Contract、Critic、Fan-out 等协议参考，不应冒充已发布 Runtime |

生产项目优先使用稳定版；只有当“改错项目、证据偷换、阻塞恢复”是主要风险时，才使用 C1.1 实验候选，并明确标记为实验生产。

## 3. 游戏项目的紧凑提示写法

不要把几十页功能清单全部塞进第一条提示。优先说明：产品、核心动词、完整闭环、必须保留、明确不做、如何证明。

```text
$loopseed one-shotted 在当前 [引擎/项目] 中制作一个可玩的 [游戏目标]。

核心闭环：
启动 → 理解目标 → 使用 [核心动作] → 得到明确反馈
→ 胜利或失败 → 立即重开。

必须保持：
[现有稳定系统、存档、物理、项目技术栈]

本轮只做：
[一个可完整体验的垂直切片]

明确不做：
[联网、商店、大量关卡、复杂剧情等]

完成证据：
真实运行一局；验证核心输入、状态变化、胜负和重开；
视觉主张必须有实际截图；未通过项必须如实报告。
```

示例：

```text
$loopseed one-shotted 在当前 Godot 项目中制作一个武侠山门迎客垂直切片。

玩家作为掌门坐在山门前，三名来客依次出现；玩家可观察、询问或拒绝，
选择会改变门派银两、声望和弟子关系，第三名来客结束后进入结算并可重开。

保持现有存档、RNG、ContentDB 和主场景结构。
本轮不做战斗、联网、商店和完整门派地图。
必须在 Godot 实际运行，证明三名来客、至少两条不同结果、结算和重开。
不得改成 HTML、静态 UI 或不可交互场景。
```

## 4. 通用项目的紧凑提示写法

```text
$loopseed one-shotted 在当前仓库中交付 [明确产品结果]。

主要用户路径：
[启动/输入] → [核心处理] → [结果] → [错误恢复或重试]

必须保持：
[现有接口、数据格式、权限、兼容性]

本轮范围：
[一个可交付闭环]

明确不做：
[非本轮内容]

完成证据：
[构建命令、测试命令、真实操作路径、产物路径]
证据不足时返回 PARTIAL 或 BLOCKED，不得用文档或代码存在冒充完成。
```

## 5. C1.1 严格绑定与机器证据

以下命令在目标项目根目录执行，`<LOOPSEED_ROOT>` 指 LOOPSEED 插件根目录。

### 初始化

```bash
python <LOOPSEED_ROOT>/skills/loopseed/scripts/one_shotted.py init \
  --root . \
  --goal "交付一个完整可玩的垂直切片"
```

### 绑定唯一验证对象

```bash
python <LOOPSEED_ROOT>/skills/loopseed/scripts/one_shotted.py bind \
  --root . \
  --project MY-PROJECT-P01 \
  --candidate "$(git rev-parse HEAD)" \
  --artifact dist/index.html
```

绑定后，项目、Commit 或主产物发生变化时必须开启新 Run，不能静默换绑。

### 增加机器 Gate

```bash
python <LOOPSEED_ROOT>/skills/loopseed/scripts/one_shotted.py add-gate \
  --root . \
  --id CORE_LOOP \
  --title "完整主循环" \
  --criterion "用户可从启动完成主流程并重开" \
  --owner lead \
  --verifier verifier \
  --machine
```

### 运行机器证据

```bash
python <LOOPSEED_ROOT>/skills/loopseed/scripts/one_shotted.py run-evidence \
  --root . \
  --gate CORE_LOOP \
  --actor verifier \
  --command "node tools/playtest.mjs" \
  --project MY-PROJECT-P01 \
  --candidate "$(git rev-parse HEAD)" \
  --artifact dist/index.html
```

机器 PASS 要求：命令退出码为 0、实际 Git HEAD 与绑定一致、验证前后产物 Hash 不变。验证器若修改或删除被验证产物，即使命令退出码为 0，也必须失败。

### 最终判断

```bash
python <LOOPSEED_ROOT>/skills/loopseed/scripts/one_shotted.py finalize --root .
```

所有必需 Gate 有合法证据、绑定仍一致、没有开放 P0/P1 后，才允许进入 `VERIFIED`。

## 6. 何时启用 Fresh Critic

默认不要为小任务增加 Critic。

值得启用：

- 游戏手感；
- 视觉重构；
- 页面首屏与完整用户流程；
- 复杂交互；
- builder 容易用自我解释掩盖真实问题的任务。

最低成本策略：

```text
先做出可运行版本
→ 最多一次 Fresh Critic
→ 只修最大的一个问题
→ 最终验收
```

Critic 应看真实产物，不先继承 builder 的辩解；视觉看截图，交互实际运行，性能必须测量。不要默认无限循环到“完美”。

## 7. 何时 Fan-out

只并行真正独立、可以分别验收的工作。

适合并行：

- 独立关卡块；
- 独立音效或文案；
- 只读调查；
- 不共享运行状态的测试夹具。

保持单一 Owner：

- 核心移动与碰撞；
- 光照、曝光、材质、后处理等耦合视觉表面；
- 网络协议与共享状态；
- 同一文件或同一架构边界。

原则：`Fan out work, not personas.`

## 8. 最低完成证据

游戏至少证明：

```text
启动 → 输入 → 状态变化 → 胜利或失败 → 重开
```

通用项目至少证明：

```text
构建/启动 → 主路径 → 可观察结果 → 错误路径或恢复 → 产物身份
```

下面这些不能单独证明完成：

- 文件存在；
- 源码看起来完整；
- README 声称通过；
- 一张截图；
- builder 自己写的总结；
- 旧日志或其他 Commit 的测试结果。

## 9. 成本纪律

- 默认一位主执行者；
- 不默认多代理；
- 不默认多次全量扫描；
- 先做最小可运行闭环；
- 聚焦测试已经证明失败时，不再跑昂贵全套测试；
- 最多一次独立 Critic 和一次针对性修复，除非新证据证明继续有价值；
- token、费用、工具调用拿不到时写 `null` 和原因，不猜测；
- 新机制若只增加文档和成本，没有阻止错误或提升产品质量，应保留更简单路线。

## 10. 常见错误用法

不要：

- 所有任务都启用 One-Shotted；
- 用视觉截图替代游戏操作验证；
- 为了实现方便把 Godot 项目改成 HTML 替代品；
- 把 Blockout 报告为视觉成品；
- 让 builder 自己批准质量 Gate；
- 在证据不足时写 COMPLETE；
- 为了并行而把耦合系统分给多个写入者；
- 把协议参考分支误称为已发布 Runtime。

## 11. 每次升级必须同步更新本文

任何满足下列条件的变更，都属于需要更新本指南的升级：

- `.codex-plugin/plugin.json` 版本变化；
- 新增、删除或重命名用户命令；
- 标准模式或 One-Shotted 行为变化；
- Gate、状态机、BLOCKED/Resume、绑定或证据规则变化；
- 稳定版、实验候选或推荐生产路线变化；
- 默认成本策略、Critic 或 Fan-out 策略变化；
- 使用示例已不再代表最新推荐。

升级提交必须同时：

1. 更新本文 front matter 中的 `loopseed_version` 和 `last_updated`；
2. 更新受影响的命令、模式选择和示例；
3. 更新 `docs/version-management.md`；
4. 必要时同步 README / README.zh-CN / CHANGELOG；
5. 运行 `python tools/verify_usage_guide_version.py`；
6. 在验证通过前不得宣称升级文档完整。

## 12. 相关文档

- [版本管理](version-management.md)
- [One-Shotted 模式](../skills/loopseed/references/one-shotted-mode.md)
- [状态合同](../skills/loopseed/references/state-contract.md)
- [运行机制阶梯](../skills/loopseed/references/runtime-ladder.md)
- [执行卡片](../skills/loopseed/references/playbook.md)
