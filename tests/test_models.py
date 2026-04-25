import pytest
from skillmesh.models.skill import Skill, SkillStep
from skillmesh.models.context import ExecutionContext, SkillResult
from skillmesh.utils.template import TemplateEngine


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
