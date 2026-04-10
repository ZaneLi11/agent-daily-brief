from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from daily_brief.domain.enums import SourceType


@dataclass(slots=True)
class FetchContext:
    since: datetime | None = None
    limit: int | None = None
    metadata: dict[str, Any] | None = None


class Source(Protocol):
    name: str
    source_type: SourceType

    def fetch(self, context: FetchContext | None = None) -> list[dict[str, Any]]:
        ...
