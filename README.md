# SkillMesh

<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/f8259f4c-9253-43ef-b6bc-9ef8415a4e17" />

> Connect and orchestrate skills across AI agents
SkillMesh is a unified skill layer for AI agents. It connects runtimes like Claude Code and OpenClaw, enabling simple orchestration without complex frameworks.
---

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
git clone https://github.com/yourname/skillmesh
cd skillmesh
pnpm install
```

---

### 2. Start API

```bash
pnpm dev:api
```

---

### 3. Run a task

```bash
curl -X POST http://localhost:3000/run \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "openclaw",
    "prompt": "Write a hello world script"
  }'
```

---

### 4. Use SDK

```ts
import { runTask } from "@skillmesh/sdk";

const result = await runTask({
  agent: "openclaw",
  prompt: "Summarize this text"
});
```

---

## 🧩 Skill Example

```yaml
name: web_search

input:
  query: string

runtime_mapping:
  openclaw: search.run
  claude: tool.search
```

---

## 🔌 Adapter Interface

```ts
export interface AgentAdapter {
  name: string;

  runTask(input: {
    prompt: string;
    skills?: string[];
  }): Promise<any>;
}
```

---

## 🎯 Roadmap

* [ ] Claude Code adapter
* [ ] Codex adapter
* [ ] Skill marketplace
* [ ] Flow builder UI
* [ ] Multi-agent orchestration

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
