import os
import json
import logging
from http import HTTPStatus
from flask import Flask, request, jsonify
from telegram import Update
from currency_bot import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app_flask = Flask(__name__)

@app_flask.route("/api/webhook", methods=["POST"])
def webhook():
    logger.info("Webhook endpoint called.")
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != os.getenv("SECRET_TOKEN"):
        logger.warning("Invalid secret token.")
        return jsonify({"error": "Invalid secret token"}), HTTPStatus.UNAUTHORIZED
    try:
        update_data = request.get_json()
        logger.info("Received update: %s", update_data)
        update = Update.de_json(update_data, app.bot)
        app.bot.initialize() if hasattr(app.bot, 'initialize') else None
        app.bot.loop.run_until_complete(app.process_update(update))
        logger.info("Update processed successfully.")
        return '', HTTPStatus.OK
    except Exception as e:
        logger.error("Error processing update: %s", str(e))
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
