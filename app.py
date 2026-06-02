```python
from flask import Flask, request
import requests
import os

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")

PHONE_NUMBER_ID = "1135928302934605"

user_state = {}
user_data = {}

# ---------------- SEND TEXT ---------------- #

def send_text(phone, message):

    url = f"https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {
            "body": message
        }
    }

    requests.post(url, headers=headers, json=payload)


# ---------------- OCCASION LIST ---------------- #

def send_occasion_list(phone):

    url = f"https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages"

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


# ---------------- BUDGET LIST ---------------- #

def send_budget_list(phone):

    url = f"https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages"

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
            "body": {
                "text": "Please select your budget"
            },
            "action": {
                "button": "Select Budget",
                "sections": [
                    {
                        "title": "Budget Range",
                        "rows": [
                            {
                                "id": "under1000",
                                "title": "Under ₹1000"
                            },
                            {
                                "id": "1000_3000",
                                "title": "₹1000 - ₹3000"
                            },
                            {
                                "id": "3000_5000",
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


# ---------------- HOME ---------------- #

@app.route("/")
def home():
    return "HampersOnly4You Bot Running"


# ---------------- WEBHOOK ---------------- #

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

        print("==============")
        print(data)
        print("==============")

        try:

            entry = data["entry"][0]
            change = entry["changes"][0]
            value = change["value"]

            if "messages" not in value:
                return "EVENT_RECEIVED", 200

            message = value["messages"][0]
            phone = message["from"]

            # LIST SELECTIONS

            if message["type"] == "interactive":

                interactive = message["interactive"]

                if interactive["type"] == "list_reply":

                    selected_id = interactive["list_reply"]["id"]
                    selected_title = interactive["list_reply"]["title"]

                    # OCCASION

                    if selected_id in [
                        "birthday",
                        "anniversary",
                        "wedding",
                        "corporate",
                        "custom"
                    ]:

                        user_data[phone] = {
                            "occasion": selected_title
                        }

                        send_budget_list(phone)

                    # BUDGET

                    elif selected_id in [
                        "under1000",
                        "1000_3000",
                        "3000_5000",
                        "5000plus"
                    ]:

                        user_data[phone]["budget"] = selected_title
                        user_state[phone] = "waiting_details"

                        send_text(
                            phone,
                            """🌸 Please share the following details:

Quantity -
Date of requirement -
Location -

You may send everything in one message.

OR

Send multiple messages and type DONE when finished."""
                        )

            # TEXT MESSAGES

            elif message["type"] == "text":

                text = message["text"]["body"].strip()

                state = user_state.get(phone)

                # Collect details

                if state == "waiting_details":

                    if "details" not in user_data[phone]:
                        user_data[phone]["details"] = []

                    if text.upper() == "DONE":

                        details = "\n".join(
                            user_data[phone]["details"]
                        )

                        reply = f"""✅ Thank you.

Our team will contact you shortly.

Lead Summary

{details}

Occasion - {user_data[phone]['occasion']}
Budget per hamper - {user_data[phone]['budget']}
"""

                        send_text(phone, reply)

                        user_state.pop(phone, None)
                        user_data.pop(phone, None)

                    else:

                        user_data[phone]["details"].append(text)

                else:

                    # Start conversation
                    send_occasion_list(phone)

        except Exception as e:
            print("ERROR:", e)

        return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
```
