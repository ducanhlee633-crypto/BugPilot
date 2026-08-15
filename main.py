from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
import json
import requests
from dotenv import load_dotenv
from schemas import Clone_repo, Delete_folder, Prompt
from tools.clone_repo import clone_repo
from tools.delete_folder import delete_folder
from tools.list_files import list_files
from tools.read_file import read_file
from tools.run_command import run_command
from tools.tool_kit import TOOLS
from system_prompt import SYSTEM_PROMPT
app = FastAPI()
load_dotenv()

PROJECTS_DIR = Path("projects")


@app.get("/", include_in_schema=False)
def ui():
    return FileResponse("ui/index.html")


@app.get("/repos", include_in_schema=False)
def list_repos():
    PROJECTS_DIR.mkdir(exist_ok=True)
    return sorted(
        p.name for p in PROJECTS_DIR.iterdir()
        if p.is_dir() and not p.name.startswith(".")
    )


app.mount("/static", StaticFiles(directory="ui"), name="static")

URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
MODEL = "gemini-3.5-flash-lite"
API_KEY = os.getenv("GEMINI_API_KEY")

# ánh xạ tên tool (khai báo trong TOOLS) -> hàm Python thật
TOOL_FUNCTIONS = {
    "list_files": list_files,
    "read_file": read_file,
    "run_command": run_command, 
}


@app.post("/clone_repo")
def clone_repo_endpoint(url: Clone_repo):
    try:
        return {"message": clone_repo(url.url)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clone failed: {e}")


@app.post("/delete_repo")
def delete_repo_endpoint(folder: Delete_folder):
    try:
        return {"message": delete_folder(folder.folder)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {e}")


def call_llm(messages):
    try:
        response = requests.post(
            url=URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": messages,
                "tools": TOOLS
            },
            timeout=60
        )
    except requests.exceptions.Timeout as e:
        raise ConnectionError("LLM API timed out after 60s") from e
    except requests.exceptions.ConnectionError as e:
        raise ConnectionError("Failed to connect to LLM API") from e
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to reach LLM API: {e}") from e

    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After", "60")
        raise ConnectionError(
            f"LLM API rate limited (429). Retry-After: {retry_after}s. "
            f"Response: {response.text[:500]}"
        )
    if response.status_code != 200:
        raise ConnectionError(
            f"LLM API returned HTTP {response.status_code}: {response.text[:500]}"
        )

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError as e:
        raise ConnectionError(f"LLM API returned invalid JSON: {e}") from e

    if "error" in data:
        raise ConnectionError(f"LLM API error: {data['error']}")

    choices = data.get("choices")
    if not choices or not choices[0].get("message"):
        raise ConnectionError(f"LLM API returned unexpected response: {data}")

    return choices[0]["message"]

@app.post("/call_agent")
def call_tool(prompt:Prompt):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set in environment. Add it to .env and restart the server.")

    messages = [
        {
            "role":"user",
            "content": f"{SYSTEM_PROMPT} folled strictly the system prompt to do this task. {prompt}"
        }
    ]

    try:
        for _ in range (12):
            message = call_llm(messages)
            messages.append(message)

            if not message.get("tool_calls"):
                return message.get("content") or "(no answer from model)"
            tool_call = message["tool_calls"][0]
            function_name = tool_call["function"]["name"]
            try:
                arguments = json.loads(tool_call["function"]["arguments"])
            except (json.JSONDecodeError, TypeError) as e:
                raise ValueError(f"Invalid tool arguments JSON from model: {e}")
            func = TOOL_FUNCTIONS.get(function_name)
            if func is None:
                raise ValueError(f"Unknown tool '{function_name}'")
            try:
                result = func(**arguments)
            except TypeError as e:
                raise TypeError(f"Invalid arguments for tool '{function_name}': {e}")
            print("ARGS:", arguments)
            messages.append({
                "role":"tool",
                "tool_call_id": tool_call["id"],
                "content": str(result)
            })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")
