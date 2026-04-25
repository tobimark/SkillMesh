from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SkillResult(BaseModel):
    """Result of a skill execution."""
    skill_name: str
    step_name: Optional[str] = None
    success: bool
    output: str = ""
    error: Optional[str] = None
    duration_ms: int = 0
    timestamp: datetime = Field(default_factory=datetime.now)


class ExecutionContext(BaseModel):
    """Context passed through skill execution."""
    variables: dict[str, Any] = Field(default_factory=dict, description="Variables for template substitution")
    results: list[SkillResult] = Field(default_factory=list, description="Results from executed steps")
    logs: list[str] = Field(default_factory=list, description="Execution logs")

    def get_var(self, name: str) -> Any:
        return self.variables.get(name)

    def set_var(self, name: str, value: Any) -> None:
        self.variables[name] = value

    def add_result(self, result: SkillResult) -> None:
        self.results.append(result)

    def add_log(self, message: str) -> None:
        self.logs.append(f"[{datetime.now().isoformat()}] {message}")
