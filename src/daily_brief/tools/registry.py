from __future__ import annotations

from typing import Any

from daily_brief.domain.models import AgentContext
from daily_brief.tools.base import Tool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def call(self, name: str, input_data: dict[str, Any], context: AgentContext) -> dict[str, Any]:
        tool = self.get(name)
        if tool is None:
            raise KeyError(f"Tool '{name}' is not registered.")
        return tool.run(input_data=input_data, context=context)

    def list_names(self) -> list[str]:
        return sorted(self._tools.keys())
