import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from skillmesh.adapters.base import AgentAdapter
from skillmesh.adapters.claude_code import ClaudeCodeAdapter
from skillmesh.models.context import ExecutionContext


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
