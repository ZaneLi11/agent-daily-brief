from __future__ import annotations

from collections import Counter

from daily_brief.domain.models import AgentContext, AgentResult, Artifact, Task


class BriefingAgent:
    def __init__(self, max_items: int = 5) -> None:
        self.max_items = max_items

    def run(
        self,
        task: Task,
        artifacts: list[Artifact],
        context: AgentContext,
    ) -> AgentResult:
        selected = artifacts[: self.max_items]

        headline = f"Daily Brief: {len(selected)} highlights"
        summary = self._build_summary(task=task, selected=selected, total=len(artifacts))

        sections: list[dict[str, str]] = []
        citations: list[dict[str, str]] = []

        for index, artifact in enumerate(selected, start=1):
            section_title = artifact.title or f"Untitled Item {index}"
            section_body = artifact.summary or artifact.content[:300]
            sections.append(
                {
                    "title": section_title,
                    "content": section_body,
                    "source": artifact.source,
                }
            )
            if artifact.url:
                citations.append(
                    {
                        "title": section_title,
                        "url": artifact.url,
                        "source": artifact.source,
                    }
                )

        source_counts = Counter(item.source for item in selected)
        source_summaries = [
            {"source": source, "count": str(count)} for source, count in source_counts.items()
        ]

        return AgentResult(
            headline=headline,
            summary=summary,
            sections=sections,
            citations=citations,
            actions=[],
            source_summaries=source_summaries,
            metadata={
                "selected_count": len(selected),
                "total_count": len(artifacts),
                "run_id": context.run_id,
            },
        )

    def _build_summary(self, task: Task, selected: list[Artifact], total: int) -> str:
        if not selected:
            return f"No artifacts available for task '{task.goal}'."
        return (
            f"Prepared {len(selected)} items for goal '{task.goal}' "
            f"from {total} normalized artifacts."
        )
