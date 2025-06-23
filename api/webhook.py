import json
import os
from http import HTTPStatus
from telegram import Update
from currency_bot import app

async def __handler__(request):
    if request.method == "POST":
        if request.headers.get('X-Telegram-Bot-Api-Secret-Token') != os.getenv('SECRET_TOKEN'):
            return {
                "statusCode": HTTPStatus.UNAUTHORIZED,
                "body": json.dumps({'error': 'Invalid token'})
            }

        try:
            update_data = await request.json()
            update = Update.de_json(update_data, app.bot)
            await app.process_update(update)
            return {'statusCode': HTTPStatus.OK}
        except Exception as e:
            return {
                "statusCode": HTTPStatus.BAD_REQUEST,
                "body": json.dumps({'error': str(e)})
            }

    return {
        "statusCode": HTTPStatus.METHOD_NOT_ALLOWED,
        "body": json.dumps({'error': 'Method not allowed'})
    }
