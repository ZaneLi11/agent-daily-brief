from __future__ import annotations

from typing import Any, Protocol

from daily_brief.domain.models import AgentContext


class Tool(Protocol):
    name: str

    def run(self, input_data: dict[str, Any], context: AgentContext) -> dict[str, Any]:
        ...
