from enum import StrEnum


class SourceType(StrEnum):
    RSS = "rss"
    HACKERNEWS = "hackernews"
    GITHUB = "github"
    OTHER = "other"


class TaskType(StrEnum):
    DAILY_BRIEF = "daily_brief"


class OutputFormat(StrEnum):
    MARKDOWN = "markdown"
    PLAINTEXT = "plaintext"
    HTML = "html"
