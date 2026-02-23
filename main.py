from fastapi import FastAPI, Request
import os, requests
from datetime import datetime
import re

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Temporary in-memory store (works for testing; we'll replace with DB next)
EXPENSES = []  # each item: {"date": "YYYY-MM-DD", "amount": int, "note": str, "user": int}

@app.get("/")
def health():
    return {"status": "ok"}

def send_message(chat_id: int, text: str):
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN empty")
        return
    url = f"{TELEGRAM_API}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=20)

def parse_add(text: str):
    # Supports: "/add 1200 groceries" or "1200 groceries"
    m = re.match(r"^(?:/add\s+)?(\d+)\s+(.+)$", text.strip(), flags=re.I)
    if not m:
        return None
    return int(m.group(1)), m.group(2).strip()

@app.post("/telegram/webhook")
async def telegram_webhook(req: Request):
    update = await req.json()
    msg = update.get("message")
    if not msg:
        return {"ok": True}

    chat_id = msg["chat"]["id"]
    user_id = msg.get("from", {}).get("id", 0)
    text = (msg.get("text") or "").strip()

    if text == "/start":
        send_message(chat_id,
            "✅ Finance Bot is live!\n\n"
            "Commands:\n"
            "1) /add 1200 groceries\n"
            "2) /summary\n\n"
            "Tip: You can also send: 1200 groceries"
        )
        return {"ok": True}

    if text == "/summary":
        # This month summary
        month = datetime.now().strftime("%Y-%m")
        month_items = [e for e in EXPENSES if e["date"].startswith(month)]
        total = sum(e["amount"] for e in month_items)
        last5 = month_items[-5:]

        lines = [f"📊 Summary for {month}",
                 f"Total: ₹{total}",
                 f"Entries: {len(month_items)}",
                 ""]
        if last5:
            lines.append("Last 5:")
            for e in last5:
                lines.append(f"- {e['date']} ₹{e['amount']} {e['note']}")
        else:
            lines.append("No expenses yet. Add one using /add 1200 groceries")

        send_message(chat_id, "\n".join(lines))
        return {"ok": True}

    # Try parse expense from message
    parsed = parse_add(text)
    if parsed:
        amount, note = parsed
        today = datetime.now().strftime("%Y-%m-%d")
        EXPENSES.append({"date": today, "amount": amount, "note": note, "user": user_id})
        send_message(chat_id, f"✅ Added: ₹{amount} — {note} (Date: {today})")
        return {"ok": True}

    # Default response
    send_message(chat_id, "I didn’t understand. Try /add 1200 groceries or /summary")
    return {"ok": True}
