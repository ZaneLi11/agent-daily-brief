from __future__ import annotations

from typing import Protocol

from daily_brief.domain.models import AgentContext, AgentResult, Artifact, Task


class Agent(Protocol):
    def run(
        self,
        task: Task,
        artifacts: list[Artifact],
        context: AgentContext,
    ) -> AgentResult:
        ...
