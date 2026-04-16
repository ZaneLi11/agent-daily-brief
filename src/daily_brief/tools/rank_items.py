from __future__ import annotations

from datetime import datetime
from typing import Any

from daily_brief.domain.models import AgentContext, Artifact


class RankItemsTool:
    name = "rank_items"

    def run(self, input_data: dict[str, Any], context: AgentContext) -> dict[str, Any]:
        artifacts = input_data.get("artifacts") or []
        if not isinstance(artifacts, list):
            return {"items": []}

        ranked = sorted(
            [item for item in artifacts if isinstance(item, Artifact)],
            key=self._rank_key,
            reverse=True,
        )
        return {"items": ranked}

    def _rank_key(self, artifact: Artifact) -> tuple[float, datetime]:
        score = artifact.score or 0.0
        published = artifact.published_at or datetime.min
        return (score, published)
