from __future__ import annotations

from daily_brief.domain.models import Artifact


def dedupe_artifacts(artifacts: list[Artifact]) -> list[Artifact]:
    seen_ids: set[str] = set()
    result: list[Artifact] = []

    for artifact in artifacts:
        if artifact.id in seen_ids:
            continue
        seen_ids.add(artifact.id)
        result.append(artifact)

    return result
