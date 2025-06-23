import os
from http import HTTPStatus
from telegram import Bot

async def handler(request):
    try:
        bot = Bot(token=os.getenv("API_TOKEN"))
        await bot.set_webhook(
            url=f"{os.getenv('WEBHOOK_URL')}/api/webhook",
            secret_token=os.getenv("SECRET_TOKEN")
        )
        return {
            "statusCode": HTTPStatus.OK,
            "body": "Webhook set successfully."
        }
    except Exception as e:
        return {
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "body": str(e)
        }

__handler__ = handler
