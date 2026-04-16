from __future__ import annotations

from daily_brief.domain.models import AgentContext, Artifact, Task
from daily_brief.skills.base import Skill


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        self._skills[skill.name] = skill

    def list_names(self) -> list[str]:
        return sorted(self._skills.keys())

    def apply_all(
        self,
        task: Task,
        artifacts: list[Artifact],
        context: AgentContext,
    ) -> list[Artifact]:
        result = artifacts
        for skill in self._skills.values():
            result = skill.apply(task=task, artifacts=result, context=context)
        return result
