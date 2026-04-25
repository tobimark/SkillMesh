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
