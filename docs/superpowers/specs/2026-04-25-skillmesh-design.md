# SkillMesh 设计方案 v1.0

**日期**: 2026-04-25
**状态**: 已认可（第二版）

---

## 1. 产品定位

**SkillMesh** 是一个 Python SDK，封装 Claude Code 作为执行引擎，提供 Skill 抽象层和编排能力。开发者基于 SkillMesh 二次开发自己的 AI Agent 产品（Web 服务、桌面客户端、可执行文件等）。

**核心定位**：
- SkillMesh 是 Python SDK，提供 Skill 加载和编排能力
- Claude Code 是被封装的执行单元（子进程模式）
- 面向固定、重复性的需求场景

**用户**：独立开发者，基于 SkillMesh 二次开发商业化 AI Agent

**核心价值**：
- **集成**：把 Claude Code CLI 变成 Python SDK，方便嵌入任何产品
- **编排**：把多个 Skill 组合成业务流程

---

## 1.1 为什么要封装 Claude Code？

Claude Code 本身是一个成熟的 Agent 框架，有 Skill 系统、子 Agent、工具调用等。封装后获得：

| 封装前 (Claude Code) | 封装后 (SkillMesh) |
|---------------------|-------------------|
| CLI 工具 | Python SDK |
| 单个 Skill 执行 | 多 Skill 编排 |
| 手动交互 | API/程序化调用 |
| 难以集成到产品 | 容易集成到任何产品 |

---

## 1.2 Claude Code 调用模式选择

**选择：子进程 + Bridge API 模式**

Claude Code 提供两种可编程接口：
- **QueryEngine SDK**：进程内调用，但依赖 Bun 运行时，封装复杂
- **Bridge API**：Claude Code 启动成 HTTP 服务，通过 JSON-RPC 通信

**推荐方案**：子进程调用 Claude Code CLI，通过 Bridge API 协议通信

```
SkillMesh SDK → Bridge API (HTTP) → Claude Code 子进程
```

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

## 9. Claude Code 源码研究结果

### 9.1 关键发现

**Skill 的本质**
- Skill = `type: 'prompt'` 的 Command（命令）
- 通过 `SkillTool` 执行（slash command 机制）
- 两种执行模式：
  - **inline**：Skill 内容展开成消息，插入当前对话
  - **fork**：在独立子 Agent 中执行，有自己的 token 预算

**Agent 执行机制**
- 通过 `AgentTool` 启动子 Agent
- `runAgent()` 是核心函数，返回 `AsyncGenerator<Message>`
- 支持多种模式：同进程、子进程、worktree（隔离 git 目录）、remote

**QueryEngine**
- Claude Code 的 SDK/headless 模式入口点
- 支持直接在进程内调用

### 9.2 Skill 定义格式（兼容 Claude Code）

```yaml
type: prompt
name: pr_review
description: GitHub PR 审查技能
context: fork  # 可选，决定执行模式（inline/fork）
model: sonnet  # 可选，模型覆盖

# 预加载的其他 Skill
skills:
  - other_skill
```

**字段说明**

| 字段 | 说明 |
|------|------|
| `type` | 固定为 `prompt` |
| `name` | Skill 名称 |
| `description` | Skill 描述 |
| `context` | 执行模式：`inline`（默认）或 `fork` |
| `model` | 可选的模型覆盖 |
| `skills` | 预加载的其他 Skill |

---

## 10. 待实现阶段研究的问题

- [x] Claude Code 的可编程接口（已研究：Bridge API / QueryEngine）
- [x] Claude Code Adapter 的具体实现（子进程 + Bridge API）
- [ ] Skill 之间的数据传递方式
- [ ] 模板引擎的实现（`{{变量}}` 替换）

---

## 11. 设计决策记录

| 日期 | 决策 | 原因 |
|------|------|------|
| 2026-04-25 | MVP 只支持 Claude Code | 简化实现，聚焦核心价值 |
| 2026-04-25 | 编程语言选择 Python | AI 领域主流，开发者基数大 |
| 2026-04-25 | Skill 由 YAML 定义 | 声明式，易于分享和复用 |
| 2026-04-25 | 条件执行和循环是核心 | 区别于简单 CLI 工具的关键特性 |
| 2026-04-25 | 子进程 + Bridge API 调用 | QueryEngine 依赖 Bun 运行时，封装复杂 |
| 2026-04-25 | Skill 格式兼容 Claude Code | 复用现有 Skill 生态 |
| 2026-04-25 | 核心价值 = 集成 + 编排 | CLI → SDK，多 Skill 组合 |
