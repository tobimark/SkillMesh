from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class SkillStep(BaseModel):
    """A single step within a skill."""
    name: str = Field(..., description="Unique name of this step")
    prompt: str = Field(..., description="Prompt sent to Claude Code")
    condition: Optional[str] = Field(None, description="Condition expression, e.g. '{{approved}}'")
    adapter: str = Field(default="claude_code", description="Adapter name to use")


class Skill(BaseModel):
    """A skill definition loaded from YAML."""
    name: str = Field(..., description="Skill name")
    description: Optional[str] = Field(None, description="Skill description")
    type: str = Field(default="prompt", description="Skill type, always 'prompt'")
    context: str = Field(default="inline", description="'inline' or 'fork' execution mode")
    model: Optional[str] = Field(None, description="Optional model override")
    skills: list[str] = Field(default_factory=list, description="Pre-loaded sub-skills")
    steps: list[SkillStep] = Field(default_factory=list, description="Skill steps")

    class Config:
        extra = "allow"
