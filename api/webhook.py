import os
import logging
from http import HTTPStatus
from flask import Flask, request, jsonify
from telegram import Update
from currency_bot import app as tg_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/api/webhook", methods=["POST"])
def webhook():
    logger.info("Webhook endpoint called.")
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != os.getenv("SECRET_TOKEN"):
        logger.warning("Invalid secret token.")
        return jsonify({"error": "Invalid secret token"}), HTTPStatus.UNAUTHORIZED
    try:
        update_data = request.get_json()
        logger.info("Received update: %s", update_data)
        update = Update.de_json(update_data, tg_app.bot)
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        if loop.is_running():
            # In rare serverless cases, create a new loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        # Initialize the application if not already done
        if not getattr(tg_app, '_initialized', False):
            loop.run_until_complete(tg_app.initialize())
        loop.run_until_complete(tg_app.process_update(update))
        logger.info("Update processed successfully.")
        return '', HTTPStatus.OK
    except Exception as e:
        logger.error("Error processing update: %s", str(e))
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
