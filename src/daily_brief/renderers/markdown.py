from __future__ import annotations

from daily_brief.domain.models import AgentResult


def render_markdown(result: AgentResult) -> str:
    lines: list[str] = []

    lines.append(f"# {result.headline}")
    lines.append("")
    lines.append(result.summary)
    lines.append("")

    if result.sections:
        lines.append("## Highlights")
        lines.append("")
        for section in result.sections:
            title = str(section.get("title") or "Untitled")
            content = str(section.get("content") or "").strip()
            source = str(section.get("source") or "").strip()

            lines.append(f"### {title}")
            if source:
                lines.append(f"- Source: {source}")
            if content:
                lines.append(content)
            lines.append("")

    if result.citations:
        lines.append("## Citations")
        lines.append("")
        for citation in result.citations:
            title = str(citation.get("title") or "Source")
            url = str(citation.get("url") or "").strip()
            source = str(citation.get("source") or "").strip()
            if url:
                if source:
                    lines.append(f"- [{title}]({url}) ({source})")
                else:
                    lines.append(f"- [{title}]({url})")
        lines.append("")

    if result.actions:
        lines.append("## Actions")
        lines.append("")
        for action in result.actions:
            lines.append(f"- {action}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"
