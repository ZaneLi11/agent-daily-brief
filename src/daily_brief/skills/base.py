from __future__ import annotations

from typing import Protocol

from daily_brief.domain.models import AgentContext, Artifact, Task


class Skill(Protocol):
    name: str

    def apply(
        self,
        task: Task,
        artifacts: list[Artifact],
        context: AgentContext,
    ) -> list[Artifact]:
        ...
