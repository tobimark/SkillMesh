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
                if TemplateEngine.evaluate_condition(
                    step.condition, context.variables
                ):
                    context.add_log(f"Skipping step: {step.name} (condition true)")
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