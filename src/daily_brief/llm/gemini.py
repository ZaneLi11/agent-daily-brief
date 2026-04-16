from __future__ import annotations

import json
import os
from collections import Counter
from datetime import datetime
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from daily_brief.domain.models import AgentContext, AgentResult, Artifact, Task


class GeminiLLM:
    name = "gemini"

    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        api_key_env: str = "GEMINI_API_KEY",
        timeout: int = 30,
        max_items: int = 10,
    ) -> None:
        self.model = model
        self.api_key_env = api_key_env
        self.timeout = timeout
        self.max_items = max_items

    def generate(
        self,
        task: Task,
        artifacts: list[Artifact],
        context: AgentContext,
    ) -> AgentResult:
        api_key = os.getenv(self.api_key_env, "").strip()
        if not api_key:
            raise RuntimeError(f"{self.api_key_env} is not set.")

        ranked = self._rank_with_tools(artifacts=artifacts, context=context)
        selected = ranked[: self.max_items]
        if not selected:
            return AgentResult(
                headline="Daily Brief: 0 highlights",
                summary=f"No artifacts available for goal '{task.goal}'.",
                metadata={"llm": self.name, "model": self.model, "run_id": context.run_id},
            )

        prompt = self._build_prompt(task=task, artifacts=selected)
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.2,
            },
        }

        response_json = self._generate_content(api_key=api_key, payload=payload)
        text = self._extract_text(response_json)
        data = self._parse_json_text(text)
        return self._to_agent_result(data=data, selected=selected, context=context)

    def _generate_content(self, api_key: str, payload: dict[str, Any]) -> dict[str, Any]:
        endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent"
        )
        body = json.dumps(payload).encode("utf-8")
        request = Request(
            endpoint,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": api_key,
                "User-Agent": "agent-daily-brief/0.1",
            },
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Gemini API HTTP error {exc.code}: {detail}") from exc
        except URLError as exc:
            raise RuntimeError(f"Gemini API network error: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise RuntimeError("Gemini API returned non-JSON response.") from exc

    def _extract_text(self, data: dict[str, Any]) -> str:
        candidates = data.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            raise RuntimeError("Gemini API returned no candidates.")

        first = candidates[0]
        content = first.get("content", {})
        parts = content.get("parts", [])
        texts: list[str] = []
        if isinstance(parts, list):
            for part in parts:
                if isinstance(part, dict):
                    text = part.get("text")
                    if isinstance(text, str) and text.strip():
                        texts.append(text.strip())

        if not texts:
            raise RuntimeError("Gemini candidate did not contain text output.")
        return "\n".join(texts)

    def _parse_json_text(self, text: str) -> dict[str, Any]:
        raw = text.strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            raw = raw.replace("json", "", 1).strip()

        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

        return {
            "headline": "Daily Brief",
            "summary": text.strip(),
            "sections": [],
            "citations": [],
            "actions": [],
            "source_summaries": [],
            "metadata": {"fallback_mode": "text_to_summary"},
        }

    def _to_agent_result(
        self,
        data: dict[str, Any],
        selected: list[Artifact],
        context: AgentContext,
    ) -> AgentResult:
        source_counts = Counter(item.source for item in selected)
        fallback_source_summaries = [
            {"source": source, "count": str(count)} for source, count in source_counts.items()
        ]

        return AgentResult(
            headline=str(data.get("headline") or f"Daily Brief: {len(selected)} highlights"),
            summary=str(data.get("summary") or ""),
            sections=self._as_list_of_dicts(data.get("sections")),
            citations=self._as_list_of_dicts(data.get("citations")),
            actions=self._as_list_of_strings(data.get("actions")),
            source_summaries=self._as_list_of_dicts(data.get("source_summaries"))
            or fallback_source_summaries,
            metadata={
                "llm": self.name,
                "model": self.model,
                "run_id": context.run_id,
                "generated_at": datetime.utcnow().isoformat(),
                **(data.get("metadata") if isinstance(data.get("metadata"), dict) else {}),
            },
        )

    def _as_list_of_dicts(self, value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        return [item for item in value if isinstance(item, dict)]

    def _as_list_of_strings(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item) for item in value]

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

    def _build_prompt(self, task: Task, artifacts: list[Artifact]) -> str:
        lines = [
            "You are a daily briefing assistant.",
            "Summarize the artifacts into concise actionable updates.",
            "Return strict JSON with keys:",
            "headline, summary, sections, citations, actions, source_summaries, metadata",
            "sections: list of {title, content, source}",
            "citations: list of {title, url, source}",
            "actions: list of short strings",
            "source_summaries: list of {source, count}",
            "",
            f"Goal: {task.goal}",
            f"Audience: {task.audience or 'general'}",
            "",
            "Artifacts:",
        ]

        for idx, item in enumerate(artifacts, start=1):
            lines.extend(
                [
                    f"{idx}. title: {item.title}",
                    f"   source: {item.source}",
                    f"   published_at: {item.published_at.isoformat() if item.published_at else 'unknown'}",
                    f"   url: {item.url or ''}",
                    f"   content: {(item.summary or item.content)[:800]}",
                ]
            )

        return "\n".join(lines)
