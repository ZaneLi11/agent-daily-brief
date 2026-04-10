from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from daily_brief.domain.enums import OutputFormat, SourceType, TaskType

@dataclass(slots=True)
class Artifact:
    id: str
    source: str
    source_type: SourceType
    title: str
    content: str
    summary: str | None = None
    url: str | None = None
    author: str | None = None
    published_at: datetime | None = None
    tags: list[str] = field(default_factory=list)
    score: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Task:
    type: TaskType
    goal: str
    audience: str | None = None
    constraints: dict[str, Any] = field(default_factory=dict)
    output_format: OutputFormat = OutputFormat.MARKDOWN
    date: datetime | None = None


@dataclass(slots=True)
class AgentContext:
    settings: Any | None = None
    llm: Any | None = None
    tool_registry: Any | None = None
    skill_registry: Any | None = None
    run_id: str | None = None
    current_time: datetime | None = None
    logger: Any | None = None


@dataclass(slots=True)
class AgentResult:
    headline: str
    summary: str
    sections: list[dict[str, Any]] = field(default_factory=list)
    citations: list[dict[str, Any]] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    source_summaries: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
