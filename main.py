from fastapi import FastAPI, Request
import os
import requests

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

@app.get("/")
def health():
    return {"status": "ok"}

def send_message(chat_id: int, text: str):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload, timeout=20)

@app.post("/telegram/webhook")
async def telegram_webhook(req: Request):
    update = await req.json()

    # Telegram sends different update types; we handle normal messages first
    message = update.get("message")
    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    text = (message.get("text") or "").strip()

    # Commands
    if text == "/start":
        send_message(chat_id,
                     "✅ Hello! I’m your Finance Bot.\n\n"
                     "Try:\n"
                     "/help\n"
                     "Or send: 1200 groceries")
        return {"ok": True}

    if text == "/help":
        send_message(chat_id,
                     "📌 Commands:\n"
                     "/start - welcome\n"
                     "/help - this message\n\n"
                     "Send an expense like:\n"
                     "1200 groceries")
        return {"ok": True}

    # Default: echo back (temporary)
    send_message(chat_id, f"📝 Received: {text}")
    return {"ok": True}
