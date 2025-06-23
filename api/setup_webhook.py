import os
from flask import Flask, jsonify
from telegram import Bot

app = Flask(__name__)

@app.route("/api/setup-webhook", methods=["GET"])
def setup_webhook():
    try:
        bot = Bot(token=os.getenv("API_TOKEN"))
        bot.set_webhook(
            url=f"{os.getenv('WEBHOOK_URL')}/api/webhook",
            secret_token=os.getenv("SECRET_TOKEN")
        )
        return jsonify({"status": "ok", "message": "Webhook set successfully."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
