from fastapi import FastAPI, Request
import os

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/telegram/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    print(data)
    return {"ok": True}