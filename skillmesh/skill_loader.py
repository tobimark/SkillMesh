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