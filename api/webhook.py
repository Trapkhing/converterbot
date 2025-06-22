import json
from http import HTTPStatus
from currency_bot import app
from telegram import Update
import os

async def handler(request):
    if request.method == "POST":
        # Get the secret token from headers
        incoming_token = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
        expected_token = os.getenv('SECRET_TOKEN')
        
        # Verify the token
        if incoming_token != expected_token:
            return {
                'statusCode': HTTPStatus.UNAUTHORIZED,
                'body': json.dumps({'status': 'unauthorized'})
            }
        
        # Process the update
        update = Update.de_json(await request.json(), app.bot)
        await app.process_update(update)
        return {
            'statusCode': HTTPStatus.OK,
            'body': json.dumps({'status': 'ok'})
        }
    
    return {
        'statusCode': HTTPStatus.METHOD_NOT_ALLOWED,
        'body': json.dumps({'status': 'method not allowed'})
    }