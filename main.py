from fastapi import FastAPI, Request
import os
import requests
import json

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/debug/getme")
def debug_getme():
    # Helps confirm BOT_TOKEN is working on Render
    if not BOT_TOKEN:
        return {"ok": False, "error": "BOT_TOKEN is empty in environment variables"}
    r = requests.get(f"{TELEGRAM_API}/getMe", timeout=20)
    return {"status_code": r.status_code, "json": r.json()}

def send_message(chat_id: int, text: str):
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN is empty. Cannot send message.")
        return

    url = f"{TELEGRAM_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    try:
        resp = requests.post(url, json=payload, timeout=20)
        print("sendMessage status:", resp.status_code)
        print("sendMessage response:", resp.text)
    except Exception as e:
        print("sendMessage exception:", str(e))

@app.post("/telegram/webhook")
async def telegram_webhook(req: Request):
    update = await req.json()

    # Log every update so we can see it in Render logs
    print("INCOMING UPDATE:", json.dumps(update)[:2000])

    message = update.get("message")
    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    text = (message.get("text") or "").strip()

    if text == "/start":
        send_message(chat_id, "✅ Bot is live! Send any message and I will reply.")
        return {"ok": True}

    send_message(chat_id, f"📝 You said: {text}")
    return {"ok": True}
