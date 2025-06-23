import os
from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route("/api/setup-webhook", methods=["GET"])
def setup_webhook():
    try:
        url = f"https://api.telegram.org/bot{os.getenv('API_TOKEN')}/setWebhook"
        data = {
            "url": f"{os.getenv('WEBHOOK_URL')}/api/webhook",
            "secret_token": os.getenv("SECRET_TOKEN")
        }
        resp = requests.post(url, data=data)
        resp.raise_for_status()
        return jsonify({"status": "ok", "message": "Webhook set successfully.", "telegram_response": resp.json()}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
