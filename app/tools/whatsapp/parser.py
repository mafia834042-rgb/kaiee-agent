def parse_whatsapp_command(message: str):
    msg = message.lower().strip()

    if "hello" in msg or "hi" in msg:
        return "GREETING"

    if "create" in msg and "agent" in msg:
        return "CREATE_AGENT"

    if "status" in msg:
        return "STATUS"

    return None