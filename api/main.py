import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from telegram import Update
from currency_bot import app as tg_app
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fastapi_app = FastAPI()

@fastapi_app.post("/api/webhook")
async def webhook(request: Request):
    logger.info("Webhook endpoint called.")
    secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret_token != os.getenv("SECRET_TOKEN"):
        logger.warning("Invalid secret token.")
        raise HTTPException(status_code=401, detail="Invalid secret token")
    try:
        update_data = await request.json()
        logger.info("Received update: %s", update_data)
        update = Update.de_json(update_data, tg_app.bot)
        # Initialize the application if not already done
        if not getattr(tg_app, '_initialized', False):
            await tg_app.initialize()
        await tg_app.process_update(update)
        logger.info("Update processed successfully.")
        return JSONResponse(content={"ok": True})
    except Exception as e:
        logger.error("Error processing update: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))

@fastapi_app.get("/api/setup-webhook")
async def setup_webhook():
    import requests
    try:
        url = f"https://api.telegram.org/bot{os.getenv('API_TOKEN')}/setWebhook"
        data = {
            "url": f"{os.getenv('WEBHOOK_URL')}/api/webhook",
            "secret_token": os.getenv("SECRET_TOKEN")
        }
        resp = requests.post(url, data=data)
        resp.raise_for_status()
        return {"status": "ok", "message": "Webhook set successfully.", "telegram_response": resp.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@fastapi_app.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return "ok"

@fastapi_app.get("/")
async def root():
    return {"status": "ok", "message": "Currency Converter Bot API"}
