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
