from __future__ import annotations

from collections import Counter

from daily_brief.domain.models import AgentContext, AgentResult, Artifact, Task


class MockLLM:
    name = "mock-llm"

    def __init__(self, max_items: int = 5) -> None:
        self.max_items = max_items

    def generate(
        self,
        task: Task,
        artifacts: list[Artifact],
        context: AgentContext,
    ) -> AgentResult:
        selected = self._rank_with_tools(artifacts=artifacts, context=context)[: self.max_items]

        sections: list[dict[str, str]] = []
        citations: list[dict[str, str]] = []

        for index, artifact in enumerate(selected, start=1):
            sections.append(
                {
                    "title": artifact.title or f"Untitled Item {index}",
                    "content": artifact.summary or artifact.content[:300],
                    "source": artifact.source,
                }
            )
            if artifact.url:
                citations.append(
                    {
                        "title": artifact.title or f"Item {index}",
                        "url": artifact.url,
                        "source": artifact.source,
                    }
                )

        source_counts = Counter(item.source for item in selected)
        source_summaries = [
            {"source": source, "count": str(count)} for source, count in source_counts.items()
        ]

        return AgentResult(
            headline=f"Daily Brief: {len(selected)} highlights",
            summary=(
                f"MockLLM prepared {len(selected)} items for goal '{task.goal}' "
                f"from {len(artifacts)} normalized artifacts."
            ),
            sections=sections,
            citations=citations,
            actions=[],
            source_summaries=source_summaries,
            metadata={
                "llm": self.name,
                "selected_count": len(selected),
                "total_count": len(artifacts),
                "run_id": context.run_id,
            },
        )

    def _rank_with_tools(self, artifacts: list[Artifact], context: AgentContext) -> list[Artifact]:
        registry = context.tool_registry
        if registry is None or not hasattr(registry, "call"):
            return artifacts

        try:
            output = registry.call("rank_items", {"artifacts": artifacts}, context=context)
        except Exception:
            return artifacts

        items = output.get("items", [])
        if isinstance(items, list) and items:
            return [item for item in items if isinstance(item, Artifact)]
        return artifacts
