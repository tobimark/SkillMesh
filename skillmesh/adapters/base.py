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
