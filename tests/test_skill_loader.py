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


@patch("httpx.get")
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