# Agentic System

A simple LangGraph template with a CLI interface.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -e .
   ```

2. **Set up environment variables:**
   Create a `.env` file in the project root with:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   LANGSMITH_API_KEY=your_langsmith_api_key_here
   LANGSMITH_PROJECT=your_project_name
   LANGSMITH_ENDPOINT=https://api.smith.langchain.com
   LANGSMITH_TRACING=true
   ```

## Usage

```bash
python cli.py
```

## Project Structure

```
src/
├── cli.py          # CLI interface using Typer
├── config.py       # Configuration and settings
├── graph.py        # Main LangGraph workflow
├── nodes.py        # Graph nodes (agent logic)
├── state.py        # State management
└── tools.py        # Tool registry (for future expansion)
```

## Architecture

The system is built around LangGraph with the following components:

1. **State Management** (`state.py`): Tracks conversation history and agent state
2. **Nodes** (`nodes.py`): Contains the agent logic for processing user input
3. **Graph** (`graph.py`): Orchestrates the workflow
5. **Tools** (`tools.py`): Registry for future tool integrations