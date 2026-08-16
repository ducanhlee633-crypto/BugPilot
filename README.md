# BugPilot

BugPilot is an AI agent that analyzes and edits cloned source code repositories. Given a natural-language task, it uses an LLM (via the Gemini API, OpenAI-compatible endpoint) to autonomously explore a repository using tools (`list_files`, `read_file`, `run_command`, `write_file`, `delete_object_in_file`) and answer questions about the code — always grounded in what it actually reads, never hallucinated.

## Features

- **AI-driven code exploration & editing** — sends a task prompt to an LLM with tool-calling enabled
- **Tool loop** — the agent calls tools, receives results, and keeps going until it has a final answer (max 12 iterations)
- **Grounding tools**:
  - `list_files` — list files in a cloned repository folder
  - `read_file` — read a file's contents
  - `run_command` — execute a read-only shell command inside a repository
  - `write_file` — create or fully overwrite a file (auto-creates parent folders)
  - `delete_object_in_file` — remove a specific content string from a file
- **Repo management** — clone repositories via URL and delete them from the `projects/` folder (with path-traversal protection)
- **Graceful error handling** — tool errors are returned to the agent as `ERROR:` messages so it can recover, and LLM API failures are caught with clear, actionable messages
- **FastAPI backend + web UI** — endpoints to trigger the agent, clone/delete repositories, and a chat-style frontend with syntax highlighting
- **Short-term memory** — agent answers are stored and reused in later sessions

## Project Structure

```
BugPilot/
├── main.py              # FastAPI app + agent loop + Gemini integration
├── schemas.py           # Pydantic request models
├── system_prompt.py     # System prompt: investigation + editing rules
├── short_memory.py      # Short-term memory for agent answers
├── tools/
│   ├── tool_kit.py      # Tool schemas advertised to the LLM (OpenAI format)
│   ├── list_files.py    # List files in a folder
│   ├── read_file.py     # Read a file
│   ├── run_command.py   # Run a shell command
│   ├── writefile.py     # Write content to a file
│   ├── modified_file.py # Delete a content string from a file
│   ├── delete_folder.py # Delete a repository folder
│   └── clone_repo.py    # Clone a git repository
├── ui/                  # Web frontend (index.html, script.js, style.css)
└── projects/            # Cloned repositories live here
    └── <repo-name>/
```

## Requirements

- Python 3.14+
- A [Gemini](https://aistudio.google.com/apikey) API key

## Setup

```bash
# 1. Create a virtual environment and install dependencies
uv sync

# 2. Set your API key
echo "GEMINI_API_KEY=your-key-here" > .env
```

## Usage

Start the server:

```bash
uv run uvicorn main:app --reload
```

Open the web UI at <http://localhost:8000> to chat with the agent or clone repos from the sidebar.

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

### Delete a repository

```bash
curl -X POST http://localhost:8000/delete_repo \
  -H "Content-Type: application/json" \
  -d '{"folder": "repo-name"}'
```

## Configuration

| Setting | Where | Description |
| --- | --- | --- |
| `GEMINI_API_KEY` | `.env` | API key for the Gemini API |
| `MODEL` | `main.py` | The model used for the agent (e.g. `gemini-3.5-flash-lite`) |
| `URL` | `main.py` | Gemini OpenAI-compatible chat completions endpoint |
| Max iterations | `main.py` | Tool-loop safety limit (default 12) |

## How It Works

1. The user sends a prompt to `/call_agent` (or via the web UI).
2. The system prompt + user prompt are sent to the LLM along with the tool schemas.
3. If the model responds with `tool_calls`, each tool is executed and its result is fed back into the conversation.
4. The loop repeats until the model answers without calling a tool, or the iteration limit is reached.
5. Tool errors (`ERROR:` messages) are returned to the agent, allowing it to correct course instead of crashing.