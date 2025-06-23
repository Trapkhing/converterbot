import os
import asyncio
from http import HTTPStatus
from telegram import Bot
from currency_bot import app

async def set_webhook():
    bot: Bot = app.bot
    await bot.set_webhook(
        url=f"{os.getenv('WEBHOOK_URL')}/api/webhook",
        secret_token=os.getenv('SECRET_TOKEN')
    )

async def __handler__(request):
    try:
        await set_webhook()
        return {
            "statusCode": HTTPStatus.OK,
            "body": "Webhook set successfully."
        }
    except Exception as e:
        return {
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "body": str(e)
        }
