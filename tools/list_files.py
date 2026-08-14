from pathlib import Path
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "nvidia/nemotron-3-super-120b-a12b:free"



def list_files(file):
    folder = Path(f"projects/{file}")

    if not folder.exists():
        raise FileNotFoundError(f"Folder 'projects/{file}' does not exist")

    if not folder.is_dir():
        raise NotADirectoryError(f"'projects/{file}' is not a directory")

    try:
        items = list(folder.iterdir())
    except PermissionError:
        raise PermissionError(f"No permission to read folder 'projects/{file}'")
    except OSError as e:
        raise OSError(f"Failed to read folder 'projects/{file}': {e}")

    return [item.name for item in items]


tools = [
    {
        "type": "function",
        "function": {
            "name": "list_files",

            "description": "List all files in folder",

            "parameters": {
                "type": "object",

                "properties": {
                    "file": {
                        "type": "string",
                        "description": "The folder name"
                    }
                },

                "required": ["file"]
            }
        }
    }
]
def call_tool(prompt):
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is not set in environment")

    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    try:
        response = requests.post(
            url=URL,

            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },

            json={
                "model": MODEL,
                "messages": messages,
                "tools": tools
            },
            timeout=60
        )
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to reach OpenRouter API: {e}")

    if response.status_code != 200:
        raise RuntimeError(
            f"OpenRouter API returned {response.status_code}: {response.text[:500]}"
        )

    try:
        data = response.json()
        message = data["choices"][0]["message"]
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected response from OpenRouter API: {e}")

    if message.get("tool_calls"):
        tool_call = message["tool_calls"][0]
        function_name = tool_call["function"]["name"]
        print("Function:", function_name)
        try:
            arguments = json.loads(
                tool_call["function"]["arguments"]
            )
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid tool arguments from LLM: {e}")
        print("Arguments:", arguments)
        if function_name == "list_files":
            result = list_files(**arguments)
        else:
            raise ValueError(f"Unknown function: {function_name}")
        print("Tool result:", result)
        messages.append(message)
        messages.append({
            "role": "tool",

            "tool_call_id": tool_call["id"],

            "content": json.dumps(result)
        })
        try:
            response = requests.post(
                url=URL,

                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },

                json={
                    "model": MODEL,
                    "messages": messages,
                    "tools": tools
                },
                timeout=60
            )
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to reach OpenRouter API: {e}")

        if response.status_code != 200:
            raise RuntimeError(
                f"OpenRouter API returned {response.status_code}: {response.text[:500]}"
            )

        try:
            final_data = response.json()
            final_message = final_data["choices"][0]["message"]
            content = final_message["content"]
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            raise RuntimeError(f"Unexpected response from OpenRouter API: {e}")

        return content
    else:
        return message.get("content")