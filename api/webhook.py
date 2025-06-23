import os
import json
from http import HTTPStatus
from telegram import Update
from currency_bot import app

async def handler(request):
    if request.method != "POST":
        return {
            "statusCode": HTTPStatus.METHOD_NOT_ALLOWED,
            "body": json.dumps({"error": "Method not allowed"})
        }

    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != os.getenv("SECRET_TOKEN"):
        return {
            "statusCode": HTTPStatus.UNAUTHORIZED,
            "body": json.dumps({"error": "Invalid secret token"})
        }

    try:
        update_data = await request.json()
        update = Update.de_json(update_data, app.bot)
        await app.process_update(update)
        return {"statusCode": HTTPStatus.OK}
    except Exception as e:
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": json.dumps({"error": str(e)})
        }

__handler__ = handler  # required by vercel
