from __future__ import annotations

from datetime import datetime

from daily_brief.domain.models import AgentContext, Artifact, Task


class PrioritizeSkill:
    name = "prioritize"

    def __init__(self, keywords: list[str] | None = None) -> None:
        self.keywords = [kw.lower() for kw in (keywords or ["ai", "agent", "python", "llm"])]

    def apply(
        self,
        task: Task,
        artifacts: list[Artifact],
        context: AgentContext,
    ) -> list[Artifact]:
        boosted: list[Artifact] = []
        for artifact in artifacts:
            text = f"{artifact.title} {artifact.content}".lower()
            bonus = sum(1 for kw in self.keywords if kw in text)
            current = artifact.score or 0.0
            artifact.score = current + bonus
            boosted.append(artifact)

        return sorted(
            boosted,
            key=lambda item: (item.score or 0.0, item.published_at or datetime.min),
            reverse=True,
        )
