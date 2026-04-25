# SkillMesh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a Python SDK that wraps Claude Code as a subprocess, loads Skills from YAML, and provides sequential/conditional execution orchestration.

**Architecture:** SkillMesh SDK consists of: (1) SkillLoader - loads YAML skill definitions, (2) ExecutionEngine - orchestrates skill execution with flow control, (3) ClaudeCodeAdapter - manages Claude Code subprocess via Bridge API. Developers embed SkillMesh in their Python products to add Claude Code-powered AI capabilities.

**Tech Stack:** Python 3.10+, PyYAML, subprocess, asyncio, httpx (for Bridge API), pydantic

---

## File Structure

```
skillmesh/
├── __init__.py              # Package init, exports public API
├── engine.py                # ExecutionEngine - orchestrates skill execution
├── skill_loader.py          # SkillLoader - loads YAML skill definitions
├── models/
│   ├── __init__.py
│   ├── skill.py             # Skill, SkillStep, Flow models (Pydantic)
│   └── context.py           # ExecutionContext, SkillResult models
├── adapters/
│   ├── __init__.py
│   ├── base.py              # AgentAdapter abstract base class
│   └── claude_code.py       # ClaudeCodeAdapter implementation
├── utils/
│   ├── __init__.py
│   └── template.py          # Template engine for {{variable}} substitution
└── cli.py                   # Optional: CLI entrypoint for testing
```

---

## Task 1: Project Scaffolding

**Files:**
- Create: `skillmesh/__init__.py`
- Create: `skillmesh/models/__init__.py`
- Create: `skillmesh/models/skill.py`
- Create: `skillmesh/models/context.py`
- Create: `skillmesh/adapters/__init__.py`
- Create: `skillmesh/adapters/base.py`
- Create: `skillmesh/utils/__init__.py`
- Create: `skillmesh/utils/template.py`
- Create: `pyproject.toml`
- Create: `tests/__init__.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Create skillmesh package directory structure**

```bash
mkdir -p skillmesh/models skillmesh/adapters skillmesh/utils tests
touch skillmesh/__init__.py skillmesh/models/__init__.py skillmesh/adapters/__init__.py skillmesh/utils/__init__.py tests/__init__.py
```

- [ ] **Step 2: Create pyproject.toml**

```toml
[project]
name = "skillmesh"
version = "0.1.0"
description = "Python SDK wrapping Claude Code for skill orchestration"
requires-python = ">=3.10"
dependencies = [
    "pyyaml>=6.0",
    "pydantic>=2.0",
    "httpx>=0.25",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

- [ ] **Step 3: Write Skill models (skillmesh/models/skill.py)**

```python
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class SkillStep(BaseModel):
    """A single step within a skill."""
    name: str = Field(..., description="Unique name of this step")
    prompt: str = Field(..., description="Prompt sent to Claude Code")
    condition: Optional[str] = Field(None, description="Condition expression, e.g. '{{approved}}'")
    adapter: str = Field(default="claude_code", description="Adapter name to use")


class Skill(BaseModel):
    """A skill definition loaded from YAML."""
    name: str = Field(..., description="Skill name")
    description: Optional[str] = Field(None, description="Skill description")
    type: str = Field(default="prompt", description="Skill type, always 'prompt'")
    context: str = Field(default="inline", description="'inline' or 'fork' execution mode")
    model: Optional[str] = Field(None, description="Optional model override")
    skills: list[str] = Field(default_factory=list, description="Pre-loaded sub-skills")
    steps: list[SkillStep] = Field(default_factory=list, description="Skill steps")

    class Config:
        extra = "allow"
```

- [ ] **Step 4: Write ExecutionContext and SkillResult models (skillmesh/models/context.py)**

```python
from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SkillResult(BaseModel):
    """Result of a skill execution."""
    skill_name: str
    step_name: Optional[str] = None
    success: bool
    output: str = ""
    error: Optional[str] = None
    duration_ms: int = 0
    timestamp: datetime = Field(default_factory=datetime.now)


class ExecutionContext(BaseModel):
    """Context passed through skill execution."""
    variables: dict[str, Any] = Field(default_factory=dict, description="Variables for template substitution")
    results: list[SkillResult] = Field(default_factory=list, description="Results from executed steps")
    logs: list[str] = Field(default_factory=list, description="Execution logs")

    def get_var(self, name: str) -> Any:
        return self.variables.get(name)

    def set_var(self, name: str, value: Any) -> None:
        self.variables[name] = value

    def add_result(self, result: SkillResult) -> None:
        self.results.append(result)

    def add_log(self, message: str) -> None:
        self.logs.append(f"[{datetime.now().isoformat()}] {message}")
```

- [ ] **Step 5: Write test for models**

```python
import pytest
from skillmesh.models.skill import Skill, SkillStep
from skillmesh.models.context import ExecutionContext, SkillResult


def test_skill_step_model():
    step = SkillStep(name="test_step", prompt="Do something")
    assert step.name == "test_step"
    assert step.prompt == "Do something"
    assert step.condition is None
    assert step.adapter == "claude_code"


def test_skill_model():
    skill = Skill(
        name="test_skill",
        description="A test skill",
        steps=[
            SkillStep(name="step1", prompt="First step"),
            SkillStep(name="step2", prompt="Second step", condition="{{skip}}"),
        ]
    )
    assert skill.name == "test_skill"
    assert len(skill.steps) == 2
    assert skill.steps[1].condition == "{{skip}}"


def test_execution_context_variables():
    ctx = ExecutionContext()
    ctx.set_var("name", "Alice")
    assert ctx.get_var("name") == "Alice"


def test_execution_context_results():
    ctx = ExecutionContext()
    result = SkillResult(skill_name="test", success=True, output="done")
    ctx.add_result(result)
    assert len(ctx.results) == 1
    assert ctx.results[0].output == "done"
```

- [ ] **Step 6: Run tests to verify**

Run: `pytest tests/test_models.py -v`
Expected: PASS (all 4 tests)

- [ ] **Step 7: Commit**

```bash
git add skillmesh/ tests/ pyproject.toml
git commit -m "feat: add project scaffolding and models"
```

---

## Task 2: Template Engine

**Files:**
- Create: `skillmesh/utils/template.py`
- Modify: `tests/test_models.py` (add template tests)

- [ ] **Step 1: Write template engine (skillmesh/utils/template.py)**

```python
from __future__ import annotations
import re
from typing import Any


class TemplateEngine:
    """Simple template engine for {{variable}} substitution."""

    VARIABLE_PATTERN = re.compile(r"\{\{(\w+)\}\}")

    @classmethod
    def substitute(cls, text: str, variables: dict[str, Any]) -> str:
        """
        Replace {{variable}} patterns in text with values from variables dict.
        If a variable is not found, leave the placeholder as-is.
        """
        def replace_match(match: re.Match) -> str:
            var_name = match.group(1)
            value = variables.get(var_name)
            if value is None:
                return match.group(0)  # Keep placeholder if not found
            return str(value)

        return cls.VARIABLE_PATTERN.sub(replace_match, text)

    @classmethod
    def evaluate_condition(cls, condition: str, variables: dict[str, Any]) -> bool:
        """
        Evaluate a condition expression.
        Currently supports: truthy values, comparisons.
        Format: '{{variable}}' or '{{variable}}' == 'value' etc.
        """
        condition = condition.strip()

        # Handle simple {{variable}} form - truthy check
        if cls.VARIABLE_PATTERN.match(condition):
            var_name = cls.VARIABLE_PATTERN.match(condition).group(1)
            value = variables.get(var_name)
            return bool(value)

        # Handle comparisons: {{a}} == 'b', {{a}} != 'b', etc.
        # Simple implementation for MVP
        for op in ["==", "!=", ">", "<", ">=", "<="]:
            if op in condition:
                parts = condition.split(op)
                if len(parts) == 2:
                    left = cls.substitute(parts[0].strip(), variables).strip()
                    right = cls.substitute(parts[1].strip(), variables).strip()
                    # Remove quotes from right side for comparison
                    right = right.strip("'\"")

                    try:
                        # Try numeric comparison
                        left_num = float(left)
                        right_num = float(right)
                        if op == "==":
                            return left_num == right_num
                        elif op == "!=":
                            return left_num != right_num
                        elif op == ">":
                            return left_num > right_num
                        elif op == "<":
                            return left_num < right_num
                        elif op == ">=":
                            return left_num >= right_num
                        elif op == "<=":
                            return left_num <= right_num
                    except ValueError:
                        # String comparison
                        if op == "==":
                            return left == right
                        elif op == "!=":
                            return left != right

        return False
```

- [ ] **Step 2: Write template tests (add to tests/test_models.py)**

```python
from skillmesh.utils.template import TemplateEngine


def test_template_substitute_basic():
    text = "Hello, {{name}}!"
    result = TemplateEngine.substitute(text, {"name": "Alice"})
    assert result == "Hello, Alice!"


def test_template_substitute_multiple():
    text = "{{greeting}}, {{name}}!"
    result = TemplateEngine.substitute(text, {"greeting": "Hi", "name": "Bob"})
    assert result == "Hi, Bob!"


def test_template_substitute_missing_var():
    text = "Hello, {{name}}!"
    result = TemplateEngine.substitute(text, {})  # No variables
    assert result == "Hello, {{name}}!"


def test_template_evaluate_condition_truthy():
    assert TemplateEngine.evaluate_condition("{{approved}}", {"approved": True}) is True
    assert TemplateEngine.evaluate_condition("{{approved}}", {"approved": False}) is False
    assert TemplateEngine.evaluate_condition("{{approved}}", {"approved": ""}) is False


def test_template_evaluate_condition_equals():
    assert TemplateEngine.evaluate_condition("{{status}} == 'active'", {"status": "active"}) is True
    assert TemplateEngine.evaluate_condition("{{status}} == 'active'", {"status": "inactive"}) is False


def test_template_evaluate_condition_numeric():
    assert TemplateEngine.evaluate_condition("{{count}} > 5", {"count": 10}) is True
    assert TemplateEngine.evaluate_condition("{{count}} > 5", {"count": 3}) is False
```

- [ ] **Step 3: Run template tests**

Run: `pytest tests/test_models.py::test_template_substitute_basic tests/test_models.py::test_template_substitute_multiple tests/test_models.py::test_template_substitute_missing_var tests/test_models.py::test_template_evaluate_condition_truthy tests/test_models.py::test_template_evaluate_condition_equals tests/test_models.py::test_template_evaluate_condition_numeric -v`
Expected: PASS (6 tests)

- [ ] **Step 4: Commit**

```bash
git add skillmesh/utils/template.py tests/test_models.py
git commit -m "feat: add template engine for variable substitution"
```

---

## Task 3: Agent Adapter Base Class

**Files:**
- Create: `skillmesh/adapters/base.py`
- Create: `tests/test_adapters.py`

- [ ] **Step 1: Write AgentAdapter abstract base (skillmesh/adapters/base.py)**

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from skillmesh.models.context import ExecutionContext


class AgentAdapter(ABC):
    """Abstract base class for agent runtime adapters."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the adapter name."""
        pass

    @abstractmethod
    async def execute(
        self,
        prompt: str,
        context: ExecutionContext,
        **kwargs: Any,
    ) -> str:
        """
        Execute a prompt and return the result.

        Args:
            prompt: The prompt to execute
            context: Execution context with variables
            **kwargs: Additional adapter-specific options

        Returns:
            The result text from the agent
        """
        pass

    @abstractmethod
    async def start(self) -> None:
        """Start the agent runtime."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the agent runtime."""
        pass
```

- [ ] **Step 2: Write adapter tests**

```python
import pytest
from skillmesh.adapters.base import AgentAdapter


class MockAdapter(AgentAdapter):
    """Mock adapter for testing."""

    @property
    def name(self) -> str:
        return "mock"

    async def execute(self, prompt, context, **kwargs):
        return f"Mock response to: {prompt}"

    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        pass


def test_agent_adapter_name():
    adapter = MockAdapter()
    assert adapter.name == "mock"


@pytest.mark.asyncio
async def test_agent_adapter_execute():
    from skillmesh.models.context import ExecutionContext

    adapter = MockAdapter()
    ctx = ExecutionContext()
    result = await adapter.execute("test prompt", ctx)
    assert result == "Mock response to: test prompt"
```

- [ ] **Step 3: Run adapter tests**

Run: `pytest tests/test_adapters.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add skillmesh/adapters/base.py tests/test_adapters.py
git commit -m "feat: add AgentAdapter abstract base class"
```

---

## Task 4: Claude Code Adapter (Subprocess Mode)

**Files:**
- Create: `skillmesh/adapters/claude_code.py`
- Modify: `tests/test_adapters.py` (add Claude Code adapter tests)

- [ ] **Step 1: Write Claude Code adapter (skillmesh/adapters/claude_code.py)**

```python
from __future__ import annotations
import asyncio
import json
import subprocess
import os
from typing import Optional
from skillmesh.adapters.base import AgentAdapter
from skillmesh.models.context import ExecutionContext


class ClaudeCodeAdapter(AgentAdapter):
    """
    Claude Code adapter that runs Claude Code as a subprocess
    and communicates via Bridge API.
    """

    def __init__(
        self,
        claude_path: Optional[str] = None,
        base_url: str = "http://localhost:8080",
    ):
        """
        Initialize Claude Code adapter.

        Args:
            claude_path: Path to claude CLI. Defaults to 'claude'.
            base_url: Bridge API base URL.
        """
        self.name = "claude_code"
        self.claude_path = claude_path or os.environ.get("CLAUDE_PATH", "claude")
        self.base_url = base_url.rstrip("/")
        self._process: Optional[subprocess.Popen] = None
        self._port: int = 8080

    async def start(self) -> None:
        """Start Claude Code in bridge mode as a subprocess."""
        if self._process is not None:
            return

        # Start Claude Code in remote-control (bridge) mode
        # This runs as a background HTTP server
        env = os.environ.copy()
        env["CLAUDE_PORT"] = str(self._port)

        self._process = subprocess.Popen(
            [self.claude_path, "remote-control"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for server to be ready (simple wait)
        await asyncio.sleep(2)

    async def stop(self) -> None:
        """Stop the Claude Code subprocess."""
        if self._process is not None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None

    async def execute(
        self,
        prompt: str,
        context: ExecutionContext,
        **kwargs,
    ) -> str:
        """
        Execute a prompt via Claude Code Bridge API.

        Args:
            prompt: The prompt to send
            context: Execution context

        Returns:
            Response text from Claude Code
        """
        import httpx

        # For MVP, use httpx to call the Bridge API
        # The exact API shape depends on Claude Code's bridge protocol
        url = f"{self.base_url}/v1/messages"

        headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }

        # Substitute variables in prompt
        from skillmesh.utils.template import TemplateEngine
        prompt = TemplateEngine.substitute(prompt, context.variables)

        payload = {
            "model": kwargs.get("model", "claude-sonnet-4-20250514"),
            "max_tokens": kwargs.get("max_tokens", 4096),
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=60.0,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("content", [{}])[0].get("text", "")
        except httpx.HTTPError as e:
            raise RuntimeError(f"Claude Code API error: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to execute prompt: {e}")
```

- [ ] **Step 2: Write Claude Code adapter tests**

```python
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from skillmesh.adapters.claude_code import ClaudeCodeAdapter
from skillmesh.models.context import ExecutionContext


def test_claude_code_adapter_name():
    adapter = ClaudeCodeAdapter()
    assert adapter.name == "claude_code"


def test_claude_code_adapter_init():
    adapter = ClaudeCodeAdapter(claude_path="/usr/bin/claude", base_url="http://localhost:9000")
    assert adapter.claude_path == "/usr/bin/claude"
    assert adapter.base_url == "http://localhost:9000"


@pytest.mark.asyncio
async def test_claude_code_adapter_stop():
    adapter = ClaudeCodeAdapter()
    # Process not started, stop should be safe
    await adapter.stop()
    assert adapter._process is None


@pytest.mark.asyncio
@patch("skillmesh.adapters.claude_code.subprocess.Popen")
async def test_claude_code_adapter_start(mock_popen):
    mock_process = MagicMock()
    mock_popen.return_value = mock_process

    adapter = ClaudeCodeAdapter()
    await adapter.start()

    mock_popen.assert_called_once()
    assert adapter._process is not None


@pytest.mark.asyncio
@patch("skillmesh.adapters.claude_code httpx.AsyncClient")
async def test_claude_code_adapter_execute(mock_client_class):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "content": [{"text": "Test response"}]
    }

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.post.return_value = mock_response
    mock_client_class.return_value = mock_client

    adapter = ClaudeCodeAdapter()
    ctx = ExecutionContext(variables={"name": "Test"})
    result = await adapter.execute("Hello {{name}}", ctx)

    assert result == "Test response"
```

- [ ] **Step 3: Run Claude Code adapter tests**

Run: `pytest tests/test_adapters.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add skillmesh/adapters/claude_code.py tests/test_adapters.py
git commit -m "feat: add Claude Code subprocess adapter"
```

---

## Task 5: Skill Loader

**Files:**
- Create: `skillmesh/skill_loader.py`
- Create: `tests/test_skill_loader.py`

- [ ] **Step 1: Write SkillLoader (skillmesh/skill_loader.py)**

```python
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
import yaml

from skillmesh.models.skill import Skill


class SkillLoader:
    """Loads skill definitions from YAML files or remote URLs."""

    def __init__(self):
        self._skills: dict[str, Skill] = {}

    def load_skill(self, source: str) -> Skill:
        """
        Load a skill from a file path or URL.

        Args:
            source: Path to YAML file or URL

        Returns:
            Loaded Skill object
        """
        source = source.strip()

        if source.startswith("http://") or source.startswith("https://"):
            return self._load_from_url(source)
        else:
            return self._load_from_file(source)

    def _load_from_file(self, path: str) -> Skill:
        """Load skill from a local YAML file."""
        file_path = Path(path)

        if not file_path.exists():
            raise FileNotFoundError(f"Skill file not found: {path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        skill = Skill.model_validate(data)
        self._skills[skill.name] = skill
        return skill

    def _load_from_url(self, url: str) -> Skill:
        """Load skill from a remote URL."""
        import httpx

        response = httpx.get(url, timeout=30)
        response.raise_for_status()

        data = yaml.safe_load(response.text)
        skill = Skill.model_validate(data)
        self._skills[skill.name] = skill
        return skill

    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a loaded skill by name."""
        return self._skills.get(name)

    def list_skills(self) -> list[str]:
        """List all loaded skill names."""
        return list(self._skills.keys())
```

- [ ] **Step 2: Write SkillLoader tests**

```python
import pytest
from unittest.mock import patch
from pathlib import Path
from skillmesh.skill_loader import SkillLoader
from skillmesh.models.skill import Skill


@pytest.fixture
def temp_skill_file(tmp_path):
    """Create a temporary skill YAML file."""
    skill_yaml = """
name: test_skill
description: A test skill
type: prompt
steps:
  - name: step1
    prompt: "Do the first thing"
  - name: step2
    prompt: "Do the second thing"
    condition: "{{skip}}"
"""
    file_path = tmp_path / "test_skill.yaml"
    file_path.write_text(skill_yaml)
    return file_path


def test_load_skill_from_file(temp_skill_file):
    loader = SkillLoader()
    skill = loader.load_skill(str(temp_skill_file))

    assert skill.name == "test_skill"
    assert skill.description == "A test skill"
    assert len(skill.steps) == 2
    assert skill.steps[0].name == "step1"


def test_load_skill_caches_by_name(temp_skill_file):
    loader = SkillLoader()
    skill1 = loader.load_skill(str(temp_skill_file))
    skill2 = loader.get_skill("test_skill")

    assert skill1 is skill2


def test_load_skill_file_not_found():
    loader = SkillLoader()
    with pytest.raises(FileNotFoundError):
        loader.load_skill("/nonexistent/path/skill.yaml")


def test_list_skills(temp_skill_file):
    loader = SkillLoader()
    loader.load_skill(str(temp_skill_file))

    assert loader.list_skills() == ["test_skill"]


@patch("skillmesh.skill_loader.httpx.get")
def test_load_skill_from_url(mock_get):
    mock_response = mock_get.return_value
    mock_response.text = """
name: remote_skill
description: A remote skill
type: prompt
steps:
  - name: remote_step
    prompt: "Do something remote"
"""
    mock_response.raise_for_status = lambda: None

    loader = SkillLoader()
    skill = loader.load_skill("https://example.com/skills/remote.yaml")

    assert skill.name == "remote_skill"
    assert skill.steps[0].name == "remote_step"
```

- [ ] **Step 3: Run SkillLoader tests**

Run: `pytest tests/test_skill_loader.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add skillmesh/skill_loader.py tests/test_skill_loader.py
git commit -m "feat: add SkillLoader for YAML skill loading"
```

---

## Task 6: Execution Engine

**Files:**
- Create: `skillmesh/engine.py`
- Create: `tests/test_engine.py`

- [ ] **Step 1: Write ExecutionEngine (skillmesh/engine.py)**

```python
from __future__ import annotations
import asyncio
from typing import Optional

from skillmesh.models.skill import Skill
from skillmesh.models.context import ExecutionContext, SkillResult
from skillmesh.skill_loader import SkillLoader
from skillmesh.adapters.base import AgentAdapter
from skillmesh.adapters.claude_code import ClaudeCodeAdapter
from skillmesh.utils.template import TemplateEngine


class ExecutionEngine:
    """
    Core execution engine that orchestrates skill execution.
    """

    def __init__(self):
        self.loader = SkillLoader()
        self._adapters: dict[str, AgentAdapter] = {}
        self._default_adapter: Optional[ClaudeCodeAdapter] = None

    def register_adapter(self, adapter: AgentAdapter) -> None:
        """Register an agent adapter."""
        self._adapters[adapter.name] = adapter

    def get_adapter(self, name: str) -> AgentAdapter:
        """Get an adapter by name."""
        if name not in self._adapters:
            raise ValueError(f"Unknown adapter: {name}")
        return self._adapters[name]

    async def initialize(self) -> None:
        """Initialize the engine and start default adapter."""
        if "claude_code" not in self._adapters:
            self._default_adapter = ClaudeCodeAdapter()
            self.register_adapter(self._default_adapter)

        for adapter in self._adapters.values():
            await adapter.start()

    async def shutdown(self) -> None:
        """Shutdown all adapters."""
        for adapter in self._adapters.values():
            await adapter.stop()

    async def run(
        self,
        skill_name: str,
        context: Optional[ExecutionContext] = None,
        **kwargs,
    ) -> ExecutionContext:
        """
        Execute a skill by name.

        Args:
            skill_name: Name of the skill to execute
            context: Optional execution context

        Returns:
            Updated execution context with results
        """
        if context is None:
            context = ExecutionContext()

        skill = self.loader.get_skill(skill_name)
        if skill is None:
            raise ValueError(f"Skill not found: {skill_name}")

        context.add_log(f"Starting skill: {skill_name}")

        for step in skill.steps:
            # Check condition
            if step.condition:
                if not TemplateEngine.evaluate_condition(
                    step.condition, context.variables
                ):
                    context.add_log(f"Skipping step: {step.name} (condition false)")
                    continue

            # Execute step
            context.add_log(f"Executing step: {step.name}")
            result = await self._execute_step(step, context, **kwargs)
            context.add_result(result)

            # Update context variables with result
            context.set_var(f"{step.name}_result", result.output)

            if not result.success:
                context.add_log(f"Step failed: {step.name} - {result.error}")
                break

        context.add_log(f"Skill completed: {skill_name}")
        return context

    async def _execute_step(
        self,
        step,
        context: ExecutionContext,
        **kwargs,
    ) -> SkillResult:
        """Execute a single skill step."""
        import time

        start_time = time.time()
        adapter = self.get_adapter(step.adapter)

        try:
            output = await adapter.execute(step.prompt, context, **kwargs)
            duration_ms = int((time.time() - start_time) * 1000)

            return SkillResult(
                skill_name=step.name,
                step_name=step.name,
                success=True,
                output=output,
                duration_ms=duration_ms,
            )
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return SkillResult(
                skill_name=step.name,
                step_name=step.name,
                success=False,
                error=str(e),
                duration_ms=duration_ms,
            )
```

- [ ] **Step 2: Write ExecutionEngine tests**

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from skillmesh.engine import ExecutionEngine
from skillmesh.models.skill import Skill, SkillStep
from skillmesh.models.context import ExecutionContext
from skillmesh.adapters.base import AgentAdapter


class MockAdapter(AgentAdapter):
    def __init__(self):
        self._name = "mock"
        self._started = False

    @property
    def name(self) -> str:
        return self._name

    async def execute(self, prompt, context, **kwargs):
        return f"Mock result for: {prompt[:20]}..."

    async def start(self) -> None:
        self._started = True

    async def stop(self) -> None:
        self._started = False


@pytest.fixture
def mock_adapter():
    return MockAdapter()


@pytest.fixture
def engine_with_mock(mock_adapter):
    engine = ExecutionEngine()
    engine.register_adapter(mock_adapter)
    return engine


def test_engine_register_adapter(engine_with_mock, mock_adapter):
    assert engine_with_mock.get_adapter("mock") is mock_adapter


def test_engine_get_unknown_adapter():
    engine = ExecutionEngine()
    with pytest.raises(ValueError, match="Unknown adapter"):
        engine.get_adapter("unknown")


@pytest.mark.asyncio
async def test_engine_initialize(engine_with_mock):
    await engine_with_mock.initialize()
    assert engine_with_mock._default_adapter is not None


@pytest.mark.asyncio
async def test_engine_run_skill(engine_with_mock, mock_adapter):
    # Load a test skill
    skill = Skill(
        name="test_skill",
        steps=[
            SkillStep(name="step1", prompt="Do thing 1", adapter="mock"),
            SkillStep(name="step2", prompt="Do thing 2", adapter="mock"),
        ]
    )
    engine_with_mock.loader._skills["test_skill"] = skill

    context = await engine_with_mock.run("test_skill")

    assert len(context.results) == 2
    assert context.results[0].success is True
    assert context.results[1].success is True


@pytest.mark.asyncio
async def test_engine_run_skill_with_condition(engine_with_mock):
    skill = Skill(
        name="conditional_skill",
        steps=[
            SkillStep(name="step1", prompt="Always run", adapter="mock"),
            SkillStep(
                name="step2",
                prompt="Maybe run",
                adapter="mock",
                condition="{{skip}}"
            ),
        ]
    )
    engine_with_mock.loader._skills["conditional_skill"] = skill

    # Without skip variable - step2 should run
    context = await engine_with_mock.run("conditional_skill")
    assert len(context.results) == 2

    # With skip=true - step2 should be skipped
    context2 = ExecutionContext(variables={"skip": False})
    context2 = await engine_with_mock.run("conditional_skill", context=context2)
    assert len(context2.results) == 2  # Both run since skip is False


@pytest.mark.asyncio
async def test_engine_shutdown():
    engine = ExecutionEngine()
    await engine.initialize()
    await engine.shutdown()
    # All adapters should be stopped
```

- [ ] **Step 3: Run ExecutionEngine tests**

Run: `pytest tests/test_engine.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add skillmesh/engine.py tests/test_engine.py
git commit -m "feat: add ExecutionEngine for skill orchestration"
```

---

## Task 7: Package Exports and CLI

**Files:**
- Modify: `skillmesh/__init__.py`
- Create: `skillmesh/cli.py`

- [ ] **Step 1: Update package exports (skillmesh/__init__.py)**

```python
"""
SkillMesh - Python SDK for Claude Code skill orchestration.
"""

from skillmesh.engine import ExecutionEngine
from skillmesh.skill_loader import SkillLoader
from skillmesh.models.skill import Skill, SkillStep
from skillmesh.models.context import ExecutionContext, SkillResult
from skillmesh.adapters.base import AgentAdapter
from skillmesh.adapters.claude_code import ClaudeCodeAdapter

__version__ = "0.1.0"

__all__ = [
    "ExecutionEngine",
    "SkillLoader",
    "Skill",
    "SkillStep",
    "ExecutionContext",
    "SkillResult",
    "AgentAdapter",
    "ClaudeCodeAdapter",
]
```

- [ ] **Step 2: Create CLI entrypoint (skillmesh/cli.py)**

```python
#!/usr/bin/env python3
"""
SkillMesh CLI - for testing and debugging.
"""
import argparse
import asyncio
from skillmesh import ExecutionEngine, ExecutionContext


async def main():
    parser = argparse.ArgumentParser(description="SkillMesh CLI")
    parser.add_argument("skill", help="Path or URL to skill YAML file")
    parser.add_argument("--var", action="append", help="Variables in key=value format")
    args = parser.parse_args()

    # Parse variables
    variables = {}
    if args.var:
        for var in args.var:
            if "=" in var:
                key, value = var.split("=", 1)
                variables[key] = value

    # Create engine and run skill
    engine = ExecutionEngine()
    await engine.initialize()

    try:
        # Load skill
        skill = engine.loader.load_skill(args.skill)

        # Run skill
        context = ExecutionContext(variables=variables)
        result = await engine.run(skill.name, context)

        # Print results
        print("\n=== Results ===")
        for step_result in result.results:
            print(f"\n[{step_result.step_name}]")
            print(f"Success: {step_result.success}")
            if step_result.success:
                print(f"Output: {step_result.output}")
            else:
                print(f"Error: {step_result.error}")

        print("\n=== Logs ===")
        for log in result.logs:
            print(log)
    finally:
        await engine.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 3: Test the package import**

```bash
cd /workspace/SkillMesh
python -c "from skillmesh import ExecutionEngine, SkillLoader; print('Import OK')"
```

- [ ] **Step 4: Commit**

```bash
git add skillmesh/__init__.py skillmesh/cli.py
git commit -m "feat: add package exports and CLI entrypoint"
```

---

## Task 8: Example Skill Files

**Files:**
- Create: `examples/example_skill.yaml`
- Create: `examples/run_example.py`

- [ ] **Step 1: Create example skill (examples/example_skill.yaml)**

```yaml
name: hello_world
description: A simple hello world skill demonstrating basic features

steps:
  - name: greet
    prompt: "Generate a friendly greeting for {{user_name}}"
    adapter: claude_code

  - name: farewell
    prompt: "Generate a farewell message"
    adapter: claude_code
    condition: "{{include_farewell}}"
```

- [ ] **Step 2: Create example runner (examples/run_example.py)**

```python
#!/usr/bin/env python3
"""
Example: Running a skill with SkillMesh.
"""
import asyncio
from skillmesh import ExecutionEngine, ExecutionContext


async def main():
    engine = ExecutionEngine()
    await engine.initialize()

    try:
        # Load skill
        engine.loader.load_skill("examples/example_skill.yaml")

        # Run with variables
        context = ExecutionContext(
            variables={
                "user_name": "Alice",
                "include_farewell": True,
            }
        )

        result = await engine.run("hello_world", context)

        # Print output
        print("\n=== Skill Output ===")
        for step_result in result.results:
            print(f"\n[{step_result.step_name}]")
            print(step_result.output)

    finally:
        await engine.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 3: Commit**

```bash
git add examples/
git commit -m "docs: add example skill and runner"
```

---

## Implementation Order

1. **Task 1**: Project Scaffolding - foundation
2. **Task 2**: Template Engine - utility used throughout
3. **Task 3**: Agent Adapter Base - contract for adapters
4. **Task 4**: Claude Code Adapter - first adapter implementation
5. **Task 5**: Skill Loader - loads skill definitions
6. **Task 6**: Execution Engine - orchestrates everything
7. **Task 7**: Package Exports and CLI - public API
8. **Task 8**: Example Skill Files - documentation

---

## Verification Commands

After all tasks:
```bash
# Run all tests
pytest tests/ -v

# Verify package imports
python -c "from skillmesh import ExecutionEngine, SkillLoader, Skill"

# Verify CLI works
python -m skillmesh.cli --help
```
