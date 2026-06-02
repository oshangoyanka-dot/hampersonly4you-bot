from flask import Flask, request
import os
import requests

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")

PHONE_NUMBER_ID = "1135928302934605"


@app.route("/")
def home():
    return "Bot Running"


@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200

        return "Verification failed", 403

    if request.method == "POST":

        data = request.get_json(force=True)

        print(data, flush=True)

        try:
            message = data["entry"][0]["changes"][0]["value"]["messages"][0]
            sender = message["from"]

            send_message(
                sender,
                "Hello 👋 Welcome to HampersOnly4You."
            )

        except Exception as e:
            print("Error:", e, flush=True)

        return "EVENT_RECEIVED", 200


def send_message(to, text):

    url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": text
        }
    }

    r = requests.post(url, headers=headers, json=payload)

    print(r.status_code, flush=True)
    print(r.text, flush=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))