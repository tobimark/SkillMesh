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