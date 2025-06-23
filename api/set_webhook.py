import os
from http import HTTPStatus
from currency_bot import app

async def handler(request):
    try:
        await app.bot.set_webhook(
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
