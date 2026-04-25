# SkillMesh 设计方案 v1.0

**日期**: 2026-04-25
**状态**: 已认可

---

## 1. 产品定位

**SkillMesh** 是一个 Python SDK，作为 Claude Code 的执行引擎和任务编排层。它以 Skill 为核心，支持条件执行、循环等复杂控制流，让开发者可以快速构建可复用的 AI Agent 功能。

**核心定位**：
- SkillMesh 是执行引擎，发起 Skill 执行
- Claude Code 是被调用的执行单元
- 面向固定、重复性的需求场景

**用户**：独立开发者，基于 SkillMesh 二次开发商业化 AI Agent（Web 服务、桌面客户端、可执行文件等）

---

## 2. 核心概念

| 概念 | 说明 |
|------|------|
| **Skill** | 预定义的、可复用的任务模板，用 YAML 描述 |
| **SkillMesh Engine** | 执行引擎，负责加载 Skill、控制执行流程、调用 Claude Code |
| **Agent Adapter** | Claude Code 的适配层，负责把 Skill 指令翻译成 Claude Code 能理解的形式 |

---

## 3. 整体架构

```
┌─────────────────────────────────────────┐
│          二次开发者产品                  │
│    (Web / 桌面 / CLI / 任何 Python 应用)   │
└────────────────┬────────────────────────┘
                 │ Python SDK
┌────────────────▼────────────────────────┐
│           SkillMesh Engine              │
│  ┌─────────────────────────────────┐   │
│  │      Skill Loader               │   │
│  │      (加载 YAML Skill)          │   │
│  └────────────────┬────────────────┘   │
│                   │                      │
│  ┌────────────────▼────────────────┐   │
│  │      Execution Engine          │   │
│  │  • 顺序执行                    │   │
│  │  • 条件执行 (if/else)          │   │
│  │  • 循环 (for/while)            │   │
│  │  • 错误处理 (try/catch)        │   │
│  └────────────────┬────────────────┘   │
│                   │                      │
│  ┌────────────────▼────────────────┐   │
│  │     Claude Code Adapter         │   │
│  │     (Agent Runtime 接口)        │   │
│  └────────────────┬────────────────┘   │
└───────────────────┼─────────────────────┘
                    │ CLI / API
┌───────────────────▼─────────────────────┐
│           Claude Code                    │
└─────────────────────────────────────────┘
```

---

## 4. Skill 定义格式（YAML）

```yaml
name: pr_review
description: GitHub PR 审查技能

skills:
  - name: get_pr_info
    action: execute
    prompt: "获取 PR 的详细信息：标题、描述、文件列表"
    adapter: claude_code

  - name: analyze_changes
    action: execute
    prompt: "分析代码变更，识别潜在问题"
    adapter: claude_code
    condition: "{{has_code_changes}}"

  - name: generate_report
    action: execute
    prompt: "生成结构化的审查报告"
    adapter: claude_code

  - name: notify_slack
    action: execute
    prompt: "将审查结果发送到 Slack"
    adapter: claude_code
    condition: "{{review_approved}}"

flow:
  - skill: get_pr_info
  - skill: analyze_changes
  - skill: generate_report
  - skill: notify_slack
    condition: "{{review_approved}}"
```

### 字段说明

| 字段 | 说明 |
|------|------|
| `name` | Skill 名称，唯一标识 |
| `description` | Skill 描述 |
| `skills` | 子 Skill 定义列表 |
| `skills[].action` | 执行动作，目前支持 `execute` |
| `skills[].prompt` | 给 Claude Code 的指令 |
| `skills[].adapter` | 使用哪个 Adapter（目前只有 `claude_code`） |
| `skills[].condition` | 条件表达式，truthy 才执行 |
| `flow` | 执行流程定义 |

---

## 5. 开发者使用示例

```python
from skillmesh import SkillMesh

# 创建引擎
sm = SkillMesh()

# 加载 Skill（从 YAML 文件）
sm.load_skill("pr_review.yaml")

# 或者从远程加载
sm.load_skill("https://skillhub.io/skills/pr_review.yaml")

# 创建 Skill 实例并执行
context = {
    "pr_url": "https://github.com/owner/repo/pull/123",
    "has_code_changes": True,
    "review_approved": False
}

result = sm.run("pr_review", context=context)

# 获取结果
print(result.output)
print(result.logs)
```

---

## 6. 执行引擎核心能力

| 能力 | 说明 | 示例 |
|------|------|------|
| 顺序执行 | 按步骤依次执行 | `flow: [step1, step2, step3]` |
| 条件执行 | 根据条件决定是否执行 | `condition: "{{approved}}"` |
| 循环 | 重复执行直到满足条件 | `loop: "{{items}}"` until: `"{{count > 10}}"` |
| 错误处理 | 捕获错误并执行备用流程 | `on_error: "fallback_skill"` |
| 并行执行 | 多个 Skill 同时执行 | `parallel: [skill1, skill2]` |

---

## 7. MVP 范围

**第一版（v1.0）只做核心功能：**

- ✅ Skill YAML 定义格式
- ✅ 顺序执行
- ✅ 条件执行
- ✅ Claude Code Adapter
- ✅ 基础日志输出
- ❌ 循环（v2）
- ❌ 并行执行（v2）
- ❌ 错误处理（v2）

---

## 8. 项目结构（初步）

```
skillmesh/
├── __init__.py
├── engine.py          # 执行引擎
├── skill_loader.py   # Skill 加载器
├── adapters/
│   └── claude_code.py # Claude Code 适配器
├── models/
│   ├── skill.py       # Skill 模型
│   └── context.py     # 执行上下文
└── utils/
    └── template.py    # 模板引擎（处理 {{变量}}）
```

---

## 9. 待实现阶段研究的问题

- Claude Code 的可编程接口（需要研究 Claude Code 源码）
- Claude Code Adapter 的具体实现方式
- Skill 之间的数据传递方式
- 模板引擎的实现（`{{变量}}` 替换）

---

## 10. 设计决策记录

| 日期 | 决策 | 原因 |
|------|------|------|
| 2026-04-25 | MVP 只支持 Claude Code | 简化实现，聚焦核心价值 |
| 2026-04-25 | 编程语言选择 Python | AI 领域主流，开发者基数大 |
| 2026-04-25 | Skill 由 YAML 定义 | 声明式，易于分享和复用 |
| 2026-04-25 | 条件执行和循环是核心 | 区别于简单 CLI 工具的关键特性 |
