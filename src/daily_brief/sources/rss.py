from __future__ import annotations

from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from daily_brief.domain.enums import SourceType
from daily_brief.sources.base import FetchContext


class RSSSource:
    name = "rss"
    source_type = SourceType.RSS

    def __init__(self, feed_urls: list[str], timeout: int = 15) -> None:
        self.feed_urls = [url.strip() for url in feed_urls if url.strip()]
        self.timeout = timeout

    def fetch(self, context: FetchContext | None = None) -> list[dict[str, Any]]:
        if not self.feed_urls:
            return []

        limit = (context.limit if context else None) or 20
        records: list[dict[str, Any]] = []

        for feed_url in self.feed_urls:
            records.extend(self._fetch_single_feed(feed_url=feed_url, limit=limit))
            if len(records) >= limit:
                return records[:limit]

        return records[:limit]

    def _fetch_single_feed(self, feed_url: str, limit: int) -> list[dict[str, Any]]:
        request = Request(feed_url, headers={"User-Agent": "agent-daily-brief/0.1"})
        try:
            with urlopen(request, timeout=self.timeout) as response:
                xml_bytes = response.read()
            root = ElementTree.fromstring(xml_bytes)
        except (URLError, TimeoutError, ElementTree.ParseError) as exc:
            raise RuntimeError(f"Failed to fetch or parse RSS feed '{feed_url}': {exc}") from exc

        items = self._extract_items(root)
        records: list[dict[str, Any]] = []

        for item in items[:limit]:
            title = self._child_text(item, ["title"])
            content = self._child_text(item, ["description", "summary", "content", "content:encoded"])
            link = self._child_text(item, ["link", "id"])
            author = self._child_text(item, ["author", "dc:creator", "name"])
            published_text = self._child_text(
                item,
                ["pubDate", "published", "updated", "dc:date"],
            )

            published_at = self._parse_date(published_text)
            record_id = self._child_text(item, ["guid", "id"]) or link or f"{feed_url}:{title}"

            records.append(
                {
                    "id": record_id,
                    "title": title or "(No Title)",
                    "content": content or "",
                    "url": link,
                    "author": author,
                    "published_at": published_at,
                    "metadata": {"feed_url": feed_url},
                }
            )

        return records

    def _extract_items(self, root: ElementTree.Element) -> list[ElementTree.Element]:
        local_name = self._local_name(root.tag)

        if local_name == "rss":
            channel = root.find("./channel")
            if channel is None:
                return []
            return list(channel.findall("./item"))

        if local_name == "feed":
            return [elem for elem in root if self._local_name(elem.tag) == "entry"]

        return []

    def _child_text(self, parent: ElementTree.Element, names: list[str]) -> str | None:
        for elem in parent.iter():
            tag_name = self._local_name(elem.tag)
            for wanted in names:
                if tag_name == wanted.split(":")[-1]:
                    text = (elem.text or "").strip()
                    if text:
                        return text
                    href = elem.attrib.get("href", "").strip()
                    if href:
                        return href
        return None

    def _local_name(self, tag: str) -> str:
        if "}" in tag:
            return tag.split("}", 1)[1]
        return tag

    def _parse_date(self, value: str | None) -> datetime | None:
        if not value:
            return None
        text = value.strip()
        if not text:
            return None

        try:
            return parsedate_to_datetime(text)
        except (TypeError, ValueError):
            pass

        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
