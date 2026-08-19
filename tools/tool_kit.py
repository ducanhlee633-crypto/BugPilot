TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",

            "description": "List all files in folder",

            "parameters": {
                "type": "object",

                "properties": {
                    "folder": {
                        "type": "string",
                        "description": "The name of a subfolder inside the projects/ directory, e.g. '-ONE-PIECE-CREW-MANAGER'. Do NOT include the 'projects/' prefix."
                    }
                },

                "required": ["folder"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",

            "description": "Read file",

            "parameters": {
                "type": "object",

                "properties": {
                    "folder": {
                        "type": "string",
                        "description": "The name of a subfolder inside the projects/ directory, e.g. '-ONE-PIECE-CREW-MANAGER'. Do NOT include the 'projects/' prefix."
                    },
                    "file": {
                        "type": "string",
                        "description": "The file name or path inside the folder, e.g. 'src/main.py'"
                    }
                },

                "required": ["folder", "file"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",

            "description": "Run command",

            "parameters": {
                "type": "object",

                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command will run"
                    },
                    "folder": {
                        "type": "string",
                        "description": "The folder will run in"
                    }, 
                },
                "required": ["command","folder"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",

            "description": "Write content to a file (creates parent folders if needed)",

            "parameters": {
                "type": "object",

                "properties": {
                    "folder": {
                        "type": "string",
                        "description": "The name of a subfolder inside the projects/ directory, e.g. '-ONE-PIECE-CREW-MANAGER'. Do NOT include the 'projects/' prefix."
                    },
                    "file": {
                        "type": "string",
                        "description": "The file name or path inside the folder, e.g. 'src/main.py'"
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write"
                    }
                },

                "required": ["folder", "file", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_object_in_file",

            "description": "Delete a content string from a file (remove matching text)",

            "parameters": {
                "type": "object",

                "properties": {
                    "folder": {
                        "type": "string",
                        "description": "The name of a subfolder inside the projects/ directory, e.g. '-ONE-PIECE-CREW-MANAGER'. Do NOT include the 'projects/' prefix."
                    },
                    "file": {
                        "type": "string",
                        "description": "The file name or path inside the folder, e.g. 'src/main.py'"
                    },
                    "content": {
                        "type": "string",
                        "description": "The exact content string to delete"
                    }
                },

                "required": ["folder", "file", "content"]
            }
        }
    },
]

OBSERVE_TOOLS = [
    tool for tool in TOOLS
    if tool["function"]["name"] in {"list_files", "read_file", "run_command"}
]

ACT_TOOLS = [
    tool for tool in TOOLS
    if tool["function"]["name"] in {"write_file", "delete_object_in_file"}
]