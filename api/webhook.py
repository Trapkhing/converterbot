import os
import json
import logging
from http import HTTPStatus
from telegram import Update
from currency_bot import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handler(request):
    logger.info("Webhook endpoint called.")
    if request.method != "POST":
        logger.warning("Method not allowed: %s", request.method)
        return {
            "statusCode": HTTPStatus.METHOD_NOT_ALLOWED,
            "body": json.dumps({"error": "Method not allowed"})
        }

    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != os.getenv("SECRET_TOKEN"):
        logger.warning("Invalid secret token.")
        return {
            "statusCode": HTTPStatus.UNAUTHORIZED,
            "body": json.dumps({"error": "Invalid secret token"})
        }

    try:
        update_data = await request.json()
        logger.info("Received update: %s", update_data)
        update = Update.de_json(update_data, app.bot)
        await app.process_update(update)
        logger.info("Update processed successfully.")
        return {"statusCode": HTTPStatus.OK}
    except Exception as e:
        logger.error("Error processing update: %s", str(e))
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": json.dumps({"error": str(e)})
        }

__handler__ = handler  # required by vercel
