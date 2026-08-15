# BugPilot

BugPilot is an AI agent that analyzes cloned source code repositories. Given a natural-language task, it uses an LLM (via the OpenRouter API) to autonomously explore a repository using tools (`list_files`, `read_file`, `run_command`) and answer questions about the code — always grounded in what it actually reads, never hallucinated.

## Features

- **AI-driven code exploration** — sends a task prompt to an LLM with tool-calling enabled
- **Tool loop** — the agent calls tools, receives results, and keeps going until it has a final answer (max 10 iterations)
- **Grounding tools**:
  - `list_files` — list files in a cloned repository folder
  - `read_file` — read a file's contents
  - `run_command` — execute a shell command inside a repository
- **Graceful error handling** — tool errors are returned to the agent as `ERROR:` messages so it can recover, and OpenRouter API failures are caught with clear, actionable messages
- **FastAPI backend** — two simple endpoints to trigger the agent and to clone repositories

## Project Structure

```
BugPilot/
├── main.py              # FastAPI app + agent loop + OpenRouter integration
├── schemas.py           # Pydantic request models
├── system_prompt.py     # System prompt that enforces evidence-based answers
├── tools/
│   ├── tool_kit.py      # Tool schemas advertised to the LLM (OpenAI format)
│   ├── list_files.py    # List files in a folder
│   ├── read_file.py     # Read a file
│   ├── run_command.py   # Run a shell command
│   └── clone_repo.py    # Clone a git repository
└── projects/            # Cloned repositories live here
    └── <repo-name>/
```

## Requirements

- Python 3.14+
- An [OpenRouter](https://openrouter.ai) API key

## Setup

```bash
# 1. Create a virtual environment and install dependencies
uv sync

# 2. Set your API key
echo "OPENROUTER_API_KEY=your-key-here" > .env
```

## Usage

Start the server:

```bash
uv run uvicorn main:app --reload
```

### Clone a repository

```bash
curl -X POST http://localhost:8000/clone_repo \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/owner/repo.git"}'
```

### Ask the agent about a repository

```bash
curl -X POST http://localhost:8000/call_agent \
  -H "Content-Type: application/json" \
  -d '{"prompt": "list all the files in -ONE-PIECE-CREW-MANAGER"}'
```

The agent will call tools as needed and return a final, code-grounded answer.

## Configuration

| Setting | Where | Description |
| --- | --- | --- |
| `OPENROUTER_API_KEY` | `.env` | API key for OpenRouter |
| `MODEL` | `main.py` | The model used for the agent (e.g. `nvidia/nemotron-3-ultra-550b-a55b:free`) |
| `URL` | `main.py` | OpenRouter chat completions endpoint |
| Max iterations | `main.py` | Tool-loop safety limit (default 10) |

## How It Works

1. The user sends a prompt to `/call_agent`.
2. The system prompt + user prompt are sent to the LLM along with the tool schemas.
3. If the model responds with `tool_calls`, each tool is executed and its result is fed back into the conversation.
4. The loop repeats until the model answers without calling a tool, or the iteration limit is reached.
5. Tool errors (`ERROR:` messages) are returned to the agent, allowing it to correct course instead of crashing.
