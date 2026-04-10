from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

from daily_brief.domain.enums import SourceType
from daily_brief.domain.models import Artifact


def normalize_records(
    source_name: str,
    source_type: SourceType,
    records: list[dict[str, Any]],
) -> list[Artifact]:
    artifacts: list[Artifact] = []

    for record in records:
        title = str(record.get("title") or "").strip()
        content = _pick_content(record)
        url = _as_optional_str(record.get("url") or record.get("link"))
        artifact_id = _as_optional_str(record.get("id")) or _build_artifact_id(
            source_name=source_name,
            title=title,
            url=url,
            content=content,
        )

        artifact = Artifact(
            id=artifact_id,
            source=source_name,
            source_type=source_type,
            title=title,
            content=content,
            summary=_as_optional_str(record.get("summary")),
            url=url,
            author=_as_optional_str(record.get("author")),
            published_at=_parse_datetime(record.get("published_at")),
            tags=_as_str_list(record.get("tags")),
            score=_as_optional_float(record.get("score")),
            metadata=dict(record.get("metadata") or {}),
        )
        artifacts.append(artifact)

    return artifacts


def _pick_content(record: dict[str, Any]) -> str:
    for key in ("content", "description", "body", "text"):
        value = record.get(key)
        if value is not None:
            return str(value).strip()
    return ""


def _build_artifact_id(source_name: str, title: str, url: str | None, content: str) -> str:
    seed = f"{source_name}|{title}|{url or ''}|{content[:120]}"
    return hashlib.sha1(seed.encode("utf-8")).hexdigest()


def _parse_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def _as_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _as_optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []
