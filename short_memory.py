messages = []

def short_term_memory(message):
    if isinstance(message, str):
        message = {"role": "assistant", "content": message}
    if message.get("role") == "system" and any(
        m.get("role") == "system" and m.get("content") == message["content"]
        for m in messages
    ):
        return messages
    messages.append(message)
    print(message)
    return messages