# AI Daily Briefing Refactor Blueprint

## Goal

Refactor the project from a simple "collectors + summarizer" pipeline into an extensible "sources + ingestion + agent orchestration + delivery" architecture.

The new design should support:

- Multiple information sources
- A unified internal data model
- A main agent that can reason over all collected information
- Pluggable tools and skills
- Multiple output formats and delivery channels
- Easy future expansion to email, Outlook, X, GitHub, RSS, and other feeds

## Core Idea

All external information should first be normalized into a shared domain model.

After normalization, a main agent should receive:

- the task
- the normalized artifacts
- the runtime context
- access to registered tools
- access to registered skills

The agent is then responsible for:

- filtering
- ranking
- clustering
- summarizing
- tool use
- style adaptation
- generating the final briefing result

## Proposed Architecture

```text
src/daily_brief/
  app/
    main.py
    bootstrap.py

  domain/
    models.py
    enums.py
    exceptions.py

  sources/
    base.py
    rss.py
    hackernews.py
    github.py
    outlook.py

  ingestion/
    orchestrator.py
    normalize.py
    dedupe.py

  agents/
    base.py
    context.py
    planner.py
    briefing_agent.py

  tools/
    base.py
    registry.py
    fetch_url.py
    search_github.py
    rank_items.py
    send_email.py

  skills/
    base.py
    registry.py
    summarize_skill.py
    prioritize_skill.py
    newsletter_skill.py

  llm/
    base.py
    mock.py
    openai.py
    claude.py
    glm.py
    prompts/
      briefing.txt
      prioritization.txt

  renderers/
    markdown.py
    plaintext.py
    html.py

  delivery/
    email.py
    file.py

  config/
    settings.py
    env.py

  workflows/
    daily_brief.py

  storage/
    cache.py
    artifacts.py
```

## Execution Flow

Recommended top-level workflow:

1. `sources` fetch raw information from RSS, Hacker News, GitHub, Outlook, and other providers.
2. `ingestion` normalizes raw input into a unified `Artifact` structure.
3. `ingestion` deduplicates, merges, and tags the artifacts.
4. `workflows/daily_brief.py` builds a `Task`.
5. The main `briefing_agent` receives the `Task`, `Artifact` list, and `AgentContext`.
6. The agent optionally uses `tools` and `skills`.
7. The agent returns an `AgentResult`.
8. `renderers` convert the result into Markdown, plaintext, or HTML.
9. `delivery` sends or stores the final output.

## Core Domain Models

These models should be designed first and kept stable.

### Artifact

Represents any normalized external information unit.

Suggested fields:

- `id`
- `source`
- `source_type`
- `title`
- `content`
- `summary`
- `url`
- `author`
- `published_at`
- `tags`
- `score`
- `metadata`

### Task

Represents the user's objective for the current run.

Suggested fields:

- `type`
- `goal`
- `audience`
- `constraints`
- `output_format`
- `date`

### AgentContext

Provides runtime dependencies and execution state.

Suggested fields:

- `settings`
- `llm`
- `tool_registry`
- `skill_registry`
- `run_id`
- `current_time`
- `logger`

### AgentResult

Represents structured output from the main agent.

Suggested fields:

- `headline`
- `summary`
- `sections`
- `citations`
- `actions`
- `source_summaries`
- `metadata`

## Recommended Interfaces

### Agent

```python
class Agent(Protocol):
    def run(self, task: Task, artifacts: list[Artifact], context: AgentContext) -> AgentResult: ...
```

### Tool

```python
class Tool(Protocol):
    name: str

    def run(self, input: dict, context: AgentContext) -> dict: ...
```

### Skill

```python
class Skill(Protocol):
    name: str

    def apply(
        self,
        task: Task,
        artifacts: list[Artifact],
        context: AgentContext,
    ) -> list[Artifact]: ...
```

## Responsibilities by Layer

### `sources/`

Only responsible for data acquisition.

Should not:

- summarize
- rank
- generate final text

Should:

- fetch
- parse
- return raw source-specific records

### `ingestion/`

Responsible for transforming raw source records into internal domain objects.

Should:

- normalize to `Artifact`
- clean text
- deduplicate
- merge metadata
- tag artifacts

### `agents/`

Responsible for reasoning and orchestration.

Should:

- interpret the task
- decide what matters
- apply skills
- call tools when needed
- generate a structured result

### `tools/`

Responsible for concrete capabilities.

Examples:

- fetch extra content from a URL
- rank candidate items
- query GitHub
- send notifications

### `skills/`

Responsible for reusable behavioral policies.

Examples:

- prioritize AI engineering news
- write in newsletter style
- compress repetitive information
- produce executive-style summaries

### `renderers/`

Responsible only for output formatting.

Examples:

- Markdown briefing
- plaintext email body
- HTML newsletter

### `delivery/`

Responsible only for sending or saving outputs.

Examples:

- write to local file
- send via SMTP
- send to API endpoint

## MVP Refactor Scope

The first rebuilt version should stay intentionally small.

Recommended MVP:

- `domain`
- `sources`
- `ingestion`
- `agents`
- `renderers`
- `config`

Initial features:

- RSS source
- Hacker News source
- GitHub source
- One `BriefingAgent`
- One mock LLM backend
- One real LLM backend
- Markdown output

Avoid adding these too early:

- multi-agent workflows
- persistent memory
- database storage
- advanced scheduling
- UI
- heavy plugin systems

## Suggested First Build Order

1. Define `Artifact`, `Task`, `AgentContext`, and `AgentResult`.
2. Build `sources/base.py` and a minimal source contract.
3. Build normalization and deduplication in `ingestion/`.
4. Build `agents/base.py` and `agents/briefing_agent.py`.
5. Build a minimal `ToolRegistry` and `SkillRegistry`.
6. Add a mock LLM adapter.
7. Add Markdown rendering.
8. Add CLI entrypoint.

## Design Principles

- Keep source acquisition separate from reasoning.
- Keep domain objects stable and simple.
- Prefer composition over giant pipeline files.
- Make the agent replaceable.
- Make tools and skills pluggable through registries.
- Keep output rendering separate from business logic.
- Build the MVP so it can run without external services when needed.

## Migration Strategy

When rebuilding:

1. Start a fresh repository or a fresh branch.
2. Recreate only the new skeleton first.
3. Port collectors into `sources/` one by one.
4. Port normalization and deduplication next.
5. Replace the old summarizer with a new `BriefingAgent`.
6. Reintroduce rendering and delivery last.

## Summary

The main structural shift is:

- old model: `collect -> summarize -> render`
- new model: `collect -> normalize -> agent orchestration -> render -> deliver`

The key architectural decision is to make the agent the center of the system, not the summarizer.

That gives the project room to grow into:

- richer reasoning
- task-aware output
- tool calling
- reusable skills
- future multi-source personal briefing workflows
