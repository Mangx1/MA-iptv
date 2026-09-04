import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ALLOWED_CHAT_ID = os.getenv("CHAT_ID", "")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN belum diset")
