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
                        "description": "The folder name"
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
                    "file": {
                        "type": "string",
                        "description": "The file name"
                    }
                },

                "required": ["file"]
            }
        }
    },
]