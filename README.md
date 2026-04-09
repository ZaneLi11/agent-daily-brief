# Agent Daily Brief

An extensible AI daily briefing system that evolves from a simple "collect + summarize" pipeline into a modular architecture:

`sources -> ingestion -> agent orchestration -> render -> delivery`

## Vision

This project aims to build a personal/professional daily briefing engine that can:

- aggregate information from multiple sources (RSS, Hacker News, GitHub, and more)
- normalize all raw data into a unified domain model
- let a central agent reason over normalized artifacts
- produce briefing outputs in multiple styles and formats
- scale to new tools, skills, and delivery channels over time

## Refactor Blueprint

The architecture design is documented in:

- [REFACTOR_BLUEPRINT.md](./REFACTOR_BLUEPRINT.md)

## MVP Scope (Current Target)

Initial rebuild will focus on:

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
- one `BriefingAgent`
- one mock LLM backend
- one real LLM backend
- Markdown output

## Planned Structure

```text
src/daily_brief/
  app/
  domain/
  sources/
  ingestion/
  agents/
  tools/
  skills/
  llm/
  renderers/
  delivery/
  config/
  workflows/
  storage/
```

## Development Approach

This repository is being built incrementally.

Current workflow:

1. Define stable domain models first
2. Build minimal contracts and orchestration
3. Add one source and one runnable workflow
4. Expand capabilities step by step

## License

[MIT](./LICENSE)
