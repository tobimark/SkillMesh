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

    # Without skip variable - step2 runs (condition evaluates to False)
    context = await engine_with_mock.run("conditional_skill")
    assert len(context.results) == 2

    # With skip=True - step2 should be skipped
    context2 = ExecutionContext(variables={"skip": True})
    context2 = await engine_with_mock.run("conditional_skill", context=context2)
    assert len(context2.results) == 1  # step2 skipped since skip is True

    # With skip=False - step2 should run
    context3 = ExecutionContext(variables={"skip": False})
    context3 = await engine_with_mock.run("conditional_skill", context=context3)
    assert len(context3.results) == 2  # Both run since skip is False


@pytest.mark.asyncio
async def test_engine_shutdown():
    engine = ExecutionEngine()
    await engine.initialize()
    await engine.shutdown()
    # All adapters should be stopped