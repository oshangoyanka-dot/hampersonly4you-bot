from flask import Flask, request
import os
import json
import requests

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = "1135928302934605"

user_data = {}

# ---------------- SEND MESSAGE ---------------- #

def send_text(to, message):
    url = f"https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": message
        }
    }

    requests.post(url, headers=headers, json=payload)


def send_occasion_list(to):
    url = f"https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "👋 Welcome to HampersOnly4You"
            },
            "body": {
                "text": "Choose an Occasion"
            },
            "action": {
                "button": "View Options",
                "sections": [
                    {
                        "title": "Occasions",
                        "rows": [
                            {
                                "id": "birthday",
                                "title": "🎂 Birthday"
                            },
                            {
                                "id": "anniversary",
                                "title": "❤️ Anniversary"
                            },
                            {
                                "id": "wedding",
                                "title": "💍 Wedding"
                            },
                            {
                                "id": "corporate",
                                "title": "🏢 Corporate Gifts"
                            },
                            {
                                "id": "custom",
                                "title": "🎁 Custom Hamper"
                            }
                        ]
                    }
                ]
            }
        }
    }

    requests.post(url, headers=headers, json=payload)


def send_budget_list(to):
    url = f"https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {
                "text": "Please select your budget"
            },
            "action": {
                "button": "Select Budget",
                "sections": [
                    {
                        "title": "Budget",
                        "rows": [
                            {
                                "id": "under1000",
                                "title": "Under ₹1000"
                            },
                            {
                                "id": "1000-3000",
                                "title": "₹1000 - ₹3000"
                            },
                            {
                                "id": "3000-5000",
                                "title": "₹3000 - ₹5000"
                            },
                            {
                                "id": "5000plus",
                                "title": "₹5000+"
                            }
                        ]
                    }
                ]
            }
        }
    }

    requests.post(url, headers=headers, json=payload)


# ---------------- WEBHOOK ---------------- #

@app.route("/")
def home():
    return "HampersOnly4You Bot Running"


@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    if request.method == "GET":

        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode and token:
            if mode == "subscribe" and token == VERIFY_TOKEN:
                return challenge, 200

        return "Verification failed", 403

    if request.method == "POST":

        data = request.get_json()

        try:

            entry = data["entry"][0]
            change = entry["changes"][0]
            value = change["value"]

            if "messages" not in value:
                return "ok", 200

            message = value["messages"][0]
            sender = message["from"]

            # ---------- TEXT ---------- #

            if message["type"] == "text":

                text = message["text"]["body"].strip()

                if sender not in user_data:

                    user_data[sender] = {
                        "step": "occasion"
                    }

                    send_occasion_list(sender)

                elif user_data[sender]["step"] == "details":

                    occasion = user_data[sender]["occasion"]
                    budget = user_data[sender]["budget"]

                    summary = f"""✅ Thank you.

Our team will contact you shortly.

Lead Summary

Occasion - {occasion}
Budget per hamper - {budget}

{text}
"""

                    send_text(sender, summary)

                    del user_data[sender]

            # ---------- LIST REPLY ---------- #

            elif message["type"] == "interactive":

                reply_id = message["interactive"]["list_reply"]["id"]
                title = message["interactive"]["list_reply"]["title"]

                if sender not in user_data:
                    user_data[sender] = {}

                step = user_data[sender].get("step")

                if step == "occasion":

                    user_data[sender]["occasion"] = title
                    user_data[sender]["step"] = "budget"

                    send_budget_list(sender)

                elif step == "budget":

                    user_data[sender]["budget"] = title
                    user_data[sender]["step"] = "details"

                    send_text(
                        sender,
                        """Please share below information:

Quantity -
Date of requirement -
Location -"""
                    )

        except Exception as e:
            print("ERROR:", str(e))

        return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))