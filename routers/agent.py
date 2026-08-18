import os
import json
import httpx
from dotenv import load_dotenv
from schemas import Prompt
from tools.list_files import list_files
from tools.read_file import read_file
from tools.run_command import run_command
from tools.tool_kit import OBSERVE_TOOLS, ACT_TOOLS
from tools.modified_file import write_file, delete_object_in_file
from system_prompt import SYSTEM_PROMPT
from short_memory import short_term_memory
import asyncio
from fastapi import HTTPException, APIRouter

router = APIRouter()

load_dotenv()

URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
MODEL = "gemini-3.5-flash-lite"
API_KEY = os.getenv("GEMINI_API_KEY")

TOOL_FUNCTIONS = {
    "list_files": list_files,
    "read_file": read_file,
    "run_command": run_command,
    "write_file": write_file,
    "delete_object_in_file": delete_object_in_file,
}






async def call_llm(messages, tools):

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
                "tools": tools
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
        for _ in range(5):

            # =========================
            # OBSERVE
            # =========================

            print("=== OBSERVE ===")

            message = await call_llm(
                messages,
                OBSERVE_TOOLS
            )

            tool_calls = message.get("tool_calls", [])

            
            messages.append(message)

            for tool_call in tool_calls:

                function_name = tool_call["function"]["name"]

                arguments = json.loads(
                    tool_call["function"]["arguments"]
                )

                func = TOOL_FUNCTIONS.get(function_name)

                if func is None:
                    raise ValueError(
                        f"Unknown tool '{function_name}'"
                    )

                result = func(**arguments)

                print("OBSERVE:", function_name)
                print("ARGS:", arguments)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": str(result)
                })


            # =========================
            # THINK
            # =========================

            print("=== THINK ===")

            message = await call_llm(
                messages,
                []
            )

            messages.append(message)


            # =========================
            # ACT
            # =========================

            print("=== ACT ===")

            message = await call_llm(
                messages,
                ACT_TOOLS
            )

            messages.append(message)


            if not message.get("tool_calls"):

                result = (
                    message.get("content")
                    or "(no answer from model)"
                )

                short_term_memory({
                    "role": "assistant",
                    "content": result
                })

                return result


            # =========================
            # EXECUTE ACT TOOLS
            # =========================

            for tool_call in message["tool_calls"]:

                function_name = tool_call["function"]["name"]

                arguments = json.loads(
                    tool_call["function"]["arguments"]
                )

                func = TOOL_FUNCTIONS.get(function_name)

                if func is None:
                    raise ValueError(
                        f"Unknown tool '{function_name}'"
                    )

                result = func(**arguments)

                print("ACT:", function_name)
                print("ARGS:", arguments)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": str(result)
                })

    except Exception as e:
        raise RuntimeError(f"Agent error: {e}") from e


@router.post("")
async def call_agent_endpoint(prompt: Prompt):
    try:
        return await call_tool(prompt)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")