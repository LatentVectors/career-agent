# Technical Stack

- application_framework: Python 3.12 + Typer CLI
- database_system: SQLModel + SQLite (file DB at `data/career_agent.db`)
- javascript_framework: n/a (CLI application)
- import_strategy: n/a
- css_framework: n/a
- ui_component_library: n/a
- fonts_provider: n/a
- icon_library: n/a
- application_hosting: local CLI (no server hosting defined)
- database_hosting: local filesystem (SQLite)
- asset_hosting: local filesystem under `data/`
- deployment_solution: pip installable package (`pyproject.toml` with console script `agentic`)
- code_repository_url: [provide]

## Python Libraries
- langgraph >= 0.6
- langchain, langchain-core, langchain-openai, langchain-chroma
- pydantic >= 2, pydantic-settings
- sqlmodel
- jinja2 + weasyprint (PDF generation)
- typer, rich, loguru
- vcrpy (request recording), tqdm

## Models
- OpenAI Chat Models via LangChain `init_chat_model` (e.g., `gpt-4o`, `gpt-4o-mini`) with API key from environment.

## Observed Architecture
- Graph orchestration with LangGraph `StateGraph` and `MemorySaver` checkpointer
- Sub-agents composed under `src/agents/*`
- File-based and SQLite storage under `data/`


