from fastapi import FastAPI
import os
import json
import requests
from dotenv import load_dotenv
from schemas import Clone_repo, Prompt
from tools.clone_repo import clone_repo
from tools.list_files import list_files
from tools.read_file import read_file
from tools.tool_kit import TOOLS
from system_prompt import SYSTEM_PROMPT
app = FastAPI()
load_dotenv()

URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
API_KEY = os.getenv("OPENROUTER_API_KEY")

# ánh xạ tên tool (khai báo trong TOOLS) -> hàm Python thật
TOOL_FUNCTIONS = {
    "list_files": list_files,
    "read_file": read_file,
}


@app.post("/clone_repo")
def clone_repo_endpoint(url: Clone_repo):
    return {"message": clone_repo(url.url)}


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
        data = response.json()
        message = data["choices"][0]["message"]
        return message
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to reach OpenRouter API: {e}")

@app.post("/call_agent")
def call_tool(prompt:Prompt):
    if not API_KEY:
        raise ValueError ("OPENROUTER_API_KEY is not set in environment")

    messages = [
        {
            "role":"user",
            "content": f"{SYSTEM_PROMPT} folled strictly the system prompt to do this task. {prompt}"
        }
    ]

    for _ in range (10):
        message = call_llm(messages)
        messages.append(message)

        if not message.get("tool_calls"):
            return message.get("content")
        tool_call = message["tool_calls"][0]
        function_name = tool_call["function"]["name"]
        arguments = json.loads(
            tool_call["function"]["arguments"]
        )
        func = TOOL_FUNCTIONS.get(function_name)
        if func is None:
            raise ValueError
        result = func(**arguments)
        arguments = json.loads(tool_call["function"]["arguments"])
        print("ARGS:", arguments)
        messages.append({
            "role":"tool",
            "tool_call_id": tool_call["id"],
            "content": str(result)
        })