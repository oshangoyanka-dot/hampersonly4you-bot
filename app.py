```python
from flask import Flask, request
import requests
import os

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")

PHONE_NUMBER_ID = "1135928302934605"

user_state = {}
user_category = {}


def send_text(phone, text):
    url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": text}
    }

    requests.post(url, headers=headers, json=payload)


def send_menu(phone):
    url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "👋 Welcome to HampersOnly4You"
            },
            "body": {
                "text": "How can we help you today?"
            },
            "action": {
                "button": "View Options",
                "sections": [
                    {
                        "title": "Categories",
                        "rows": [
                            {
                                "id": "birthday",
                                "title": "Birthday Hampers"
                            },
                            {
                                "id": "anniversary",
                                "title": "Anniversary Hampers"
                            },
                            {
                                "id": "corporate",
                                "title": "Corporate Gifting"
                            },
                            {
                                "id": "custom",
                                "title": "Custom Hampers"
                            },
                            {
                                "id": "team",
                                "title": "Talk to Team"
                            }
                        ]
                    }
                ]
            }
        }
    }

    requests.post(url, headers=headers, json=payload)


@app.route("/")
def home():
    return "HampersOnly4You Bot Running"


@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200

        return "Verification failed", 403

    data = request.get_json(silent=True)

    try:
        value = data["entry"][0]["changes"][0]["value"]

        if "messages" not in value:
            return "EVENT_RECEIVED", 200

        message = value["messages"][0]
        phone = message["from"]

        if message["type"] == "interactive":

            category = message["interactive"]["list_reply"]["title"]

            user_state[phone] = "waiting_requirements"
            user_category[phone] = category

            send_text(
                phone,
                f"""🌸 {category}

Please share your requirements.

Quantity -
Date of requirement -
Location -

Example:

Quantity - 50
Date of requirement - 20 June 2026
Location - Delhi"""
            )

        elif message["type"] == "text":

            text = message["text"]["body"].strip()

            if user_state.get(phone) == "waiting_requirements":

                category = user_category.get(phone, "General Enquiry")

                summary = f"""✅ Thank you.

Our team will contact you shortly.

Lead Summary

Occasion - {category}

{text}
"""

                send_text(phone, summary)

                user_state.pop(phone, None)
                user_category.pop(phone, None)

            else:
                send_menu(phone)

    except Exception as e:
        print("ERROR:", str(e), flush=True)

    return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
```
