from __future__ import annotations

from datetime import datetime
from typing import Any

from daily_brief.agents.briefing_agent import BriefingAgent
from daily_brief.domain.enums import OutputFormat, SourceType, TaskType
from daily_brief.domain.models import AgentContext, Task
from daily_brief.ingestion.dedupe import dedupe_artifacts
from daily_brief.ingestion.normalize import normalize_records
from daily_brief.renderers.markdown import render_markdown
from daily_brief.sources.base import FetchContext
from daily_brief.sources.rss import RSSSource


def run_daily_brief_workflow() -> str:
    raw_records = _mock_records()
    return _run_pipeline(
        source_name="mock_rss",
        source_type=SourceType.RSS,
        goal="Summarize important AI and engineering updates",
        raw_records=raw_records,
    )


def run_rss_brief_workflow(feed_urls: list[str], limit: int = 20) -> str:
    source = RSSSource(feed_urls=feed_urls)
    raw_records = source.fetch(FetchContext(limit=limit))
    return _run_pipeline(
        source_name=source.name,
        source_type=source.source_type,
        goal="Summarize important updates from RSS feeds",
        raw_records=raw_records,
    )


def _run_pipeline(
    source_name: str,
    source_type: SourceType,
    goal: str,
    raw_records: list[dict[str, Any]],
) -> str:
    task = Task(
        type=TaskType.DAILY_BRIEF,
        goal=goal,
        audience="self",
        output_format=OutputFormat.MARKDOWN,
        date=datetime.utcnow(),
    )

    context = AgentContext(
        run_id=f"run-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        current_time=datetime.utcnow(),
    )

    artifacts = normalize_records(source_name=source_name, source_type=source_type, records=raw_records)
    artifacts = dedupe_artifacts(artifacts)

    agent = BriefingAgent(max_items=10)
    result = agent.run(task=task, artifacts=artifacts, context=context)

    return render_markdown(result)


def _mock_records() -> list[dict[str, Any]]:
    return [
        {
            "id": "a1",
            "title": "Open-source coding agent benchmark released",
            "description": "A new benchmark compares coding agents across bug-fix tasks.",
            "url": "https://example.com/agent-benchmark",
            "author": "Research Team",
            "published_at": "2026-04-09T08:30:00Z",
            "tags": ["agents", "benchmark"],
        },
        {
            "id": "a2",
            "title": "New Python packaging workflow gains traction",
            "description": "Teams are adopting faster, reproducible Python build flows.",
            "url": "https://example.com/python-packaging",
            "author": "Dev Weekly",
            "published_at": "2026-04-09T10:00:00Z",
            "tags": ["python", "tooling"],
        },
        {
            "id": "a2",
            "title": "New Python packaging workflow gains traction",
            "description": "Duplicate item to validate deduplication by artifact id.",
            "url": "https://example.com/python-packaging",
        },
    ]
