<p align="center">
  <img width="500" height="96" alt="微信图片_20260421174416_325_94" src="https://github.com/user-attachments/assets/b171213c-9cd1-4da4-a40f-a82c9300a3d5" />
 </p>

<p align="center">Connect and orchestrate skills across AI agents</p>
SkillMesh is a unified skill layer for AI agents. It connects runtimes like Claude Code and OpenClaw, enabling simple orchestration without complex frameworks.

## ✨ Overview

**SkillMesh** is a lightweight control layer for building AI products using existing agent runtimes.

Instead of building agents from scratch or relying on heavy frameworks like LangChain, SkillMesh lets you:

* Use existing agents (Claude Code, OpenClaw, Codex)
* Reuse and compose skills
* Ship AI features faster with less complexity

---

## ❗ The Problem

Building AI agents today is overcomplicated.

Most approaches involve:

* Heavy frameworks with too many abstractions
* Complex orchestration logic
* Difficult debugging and maintenance

At the same time, powerful agent runtimes already exist — capable of planning, tool use, and execution.

> The real challenge is not building agents.
> It’s **using them effectively to build products**.

---

## 💡 The Solution

SkillMesh provides a simple layer that sits between your app and multiple AI agents:

* Unified interface for different runtimes
* Skill-based abstraction
* Lightweight orchestration

> Don’t build agents.
> **Compose them.**

---

## 🧱 Architecture

![Architecture](./architecture.svg)

---

## 🚀 Features

### 🔌 Multi-Agent Support

* Claude Code
* OpenClaw
* Codex (planned)

---

### 🧩 Skill Layer

* Unified skill abstraction
* Cross-agent compatibility
* YAML / JSON definitions

---

### ⚙️ Lightweight Orchestration

* Simple skill chaining
* Extensible execution model

---

### 🌐 API-First

* Build your own UI or SaaS on top
* Easy backend integration

---

## ⚡ Quick Start

### 1. Install

```bash
pip install skillmesh
```

Or install from source:

```bash
git clone https://github.com/tobimark/SkillMesh.git
cd SkillMesh
pip install -e .
```

---

### 2. Create a Skill

```yaml
# examples/hello_world.yaml
name: hello_world
description: A simple hello world skill

steps:
  - name: greet
    prompt: "Generate a friendly greeting for {{user_name}}"
    adapter: claude_code
```

---

### 3. Run with Python

```python
import asyncio
from skillmesh import ExecutionEngine, ExecutionContext

async def main():
    engine = ExecutionEngine()
    await engine.initialize()

    # Load and run a skill
    engine.loader.load_skill("examples/hello_world.yaml")

    context = ExecutionContext(variables={"user_name": "Alice"})
    result = await engine.run("hello_world", context)

    for step_result in result.results:
        print(f"[{step_result.step_name}] {step_result.output}")

    await engine.shutdown()

asyncio.run(main())
```

---

## 🧩 Skill Example

```yaml
name: pr_review
description: GitHub PR 审查技能

steps:
  - name: get_pr_info
    prompt: "获取 PR 的详细信息"
    adapter: claude_code

  - name: analyze_changes
    prompt: "分析代码变更，识别潜在问题"
    adapter: claude_code
    condition: "{{has_code_changes}}"
```

---

## 🔌 Adapter Interface

```python
from abc import ABC, abstractmethod
from skillmesh.models.context import ExecutionContext

class AgentAdapter(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def execute(
        self,
        prompt: str,
        context: ExecutionContext,
        **kwargs
    ) -> str:
        pass

    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    async def stop(self) -> None:
        pass
```

---

## 🎯 Roadmap

* [x] Claude Code adapter
* [ ] OpenClaw adapter
* [ ] Codex adapter
* [ ] Loop execution
* [ ] Parallel execution
* [ ] Error handling

---

## 🧠 Philosophy

> Skills are the real abstraction.
> Agents are just runtimes.

---

## 🧑‍💻 Who is this for?

* AI product developers
* Teams building internal AI tools
* Developers who want speed over complexity

---

## 📄 License

MIT

---

## ⭐ Final Thought

The future isn’t one AI agent.

> It’s a network of capabilities.

**SkillMesh is the layer that connects them.**
