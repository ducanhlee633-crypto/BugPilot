import os
import json
import httpx
from dotenv import load_dotenv
from schemas import Prompt
from tools.list_files import list_files
from tools.read_file import read_file
from tools.run_command import run_command
from tools.tool_kit import TOOLS
from tools.modified_file import write_file, delete_object_in_file
from system_prompt import SYSTEM_PROMPT
from short_memory import short_term_memory
import asyncio
load_dotenv()

URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "qwen/qwen3.6-27b"
API_KEY = os.getenv("GROQ_API_KEY")

TOOL_FUNCTIONS = {
    "list_files": list_files,
    "read_file": read_file,
    "run_command": run_command,
    "write_file": write_file,
    "delete_object_in_file": delete_object_in_file,
}






async def call_llm(messages):
    try:
        response =  await httpx.AsyncClient().post(
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
    except httpx.TimeoutException as e:
        raise ConnectionError("LLM API timed out after 60s") from e
    except httpx.ConnectError as e:
        raise ConnectionError("Failed to connect to LLM API") from e

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
    except json.JSONDecodeError as e:
        raise ConnectionError(f"LLM API returned invalid JSON: {e}") from e

    if "error" in data:
        raise ConnectionError(f"LLM API error: {data['error']}")

    choices = data.get("choices")
    if not choices or not choices[0].get("message"):
        raise ConnectionError(f"LLM API returned unexpected response: {data}")

    return choices[0]["message"]

async def call_tool(prompt: Prompt):
    if not API_KEY:
                raise ConnectionError("OLLAMA_API_KEY is not set in environment. Add it to .env and restart the server.")
    history = short_term_memory({"role":"user","content":prompt.prompt})

    messages = [
        {"role":"system","content":SYSTEM_PROMPT},
        *[m for m in history[-10:] if m.get("role") != "system"],
    ]

    try:
        while True:
            message = await call_llm(messages)
            messages.append(message)

            if not message.get("tool_calls"):
                result =  message.get("content") or "(no answer from model)"
                short_term_memory({"role":"assistant", "content":result})
                return result
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
            await asyncio.sleep(1)
    except Exception as e:
        raise RuntimeError(f"Agent error: {e}") from e