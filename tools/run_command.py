import subprocess
import shlex
from pathlib import Path

PROJECT_ROOT = Path("projects").resolve()

MAX_OUTPUT_CHARS = 20000
TIMEOUT_SECONDS = 60
READ_ONLY_COMMANDS = {
    "pwd",
    "ls",
    "find",
    "tree",
    "cat",
    "head",
    "tail",
    "grep",
    "rg",
    "file",
    "wc",
    "sort",
    "uniq",
    "diff",
}

GIT_COMMANDS = {
    ("git", "status"),
    ("git", "diff"),
    ("git", "log"),
    ("git", "show"),
    ("git", "branch"),
    ("git", "ls-files"),
}

PYTHON_COMMANDS = {
    ("python", "--version"),
    ("python3", "--version"),
    ("python", "-m", "pytest"),
    ("python3", "-m", "pytest"),
    ("python", "-m", "compileall"),
    ("python3", "-m", "compileall"),
}

TEST_COMMANDS = {
    "pytest",
    "ruff",
    "mypy",
}

JS_COMMANDS = {
    ("node", "--version"),
    ("npm", "--version"),
    ("npm", "test"),
    ("npm", "run", "test"),
    ("npm", "run", "lint"),
    ("npm", "run", "build"),
}
def _truncate(text: str, limit: int = MAX_OUTPUT_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n...[truncated, total {len(text)} chars]"


def run_command(command:str,folder):
    try:
        target = (PROJECT_ROOT / folder).resolve()
        if not target.is_relative_to(PROJECT_ROOT):
            return f"ERROR: Folder '{folder}' is outside projects/."

        if not target.exists():
            return f"ERROR: Folder '{folder}' does not exist."

        if not target.is_dir():
            return f"ERROR: '{folder}' is not a directory."

        cmd = shlex.split(command)
        if not cmd:
            return "ERROR: Command is empty."
        cmd_t = tuple(cmd)
        # allow args: e.g. git log --oneline -10 should match ("git","log")
        allowance = (
            cmd[0] in READ_ONLY_COMMANDS
            or cmd_t[:2] in GIT_COMMANDS
            or cmd_t[:3] in PYTHON_COMMANDS or cmd_t in PYTHON_COMMANDS
            or cmd[0] in TEST_COMMANDS
            or cmd_t[:3] in JS_COMMANDS or cmd_t in JS_COMMANDS
        )
        if not allowance:
            return "ERROR: This command is not allowed"
        result = subprocess.run(
            cmd,
            cwd = target,
            capture_output=True,
            text = True,
            encoding="utf-8",
            timeout = TIMEOUT_SECONDS
        )
        return {
            "command": command,
            "returncode": result.returncode,
            "stdout": _truncate(result.stdout),
            "stderr": _truncate(result.stderr)
        }
    except subprocess.TimeoutExpired:
        return f"ERROR: Command timed out after {TIMEOUT_SECONDS}s: '{command}'"
    except OSError as e:
        return f"ERROR: Failed to run command '{command}': {e}"
    except Exception as e:
        return f"ERROR: Unexpected error running '{command}': {e}"
