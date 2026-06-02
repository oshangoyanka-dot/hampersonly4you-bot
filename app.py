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


def send_text(phone, text):

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
            "body": text
        }
    }

    requests.post(url, headers=headers, json=payload)


def send_main_menu(phone):

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
                "text": "How can we help you today?"
            },
            "action": {
                "button": "View Options",
                "sections": [
                    {
                        "title": "Choose Category",
                        "rows": [
                            {
                                "id": "birthday",
                                "title": "🎂 Birthday Hampers"
                            },
                            {
                                "id": "anniversary",
                                "title": "❤️ Anniversary Hampers"
                            },
                            {
                                "id": "corporate",
                                "title": "🏢 Corporate Gifting"
                            },
                            {
                                "id": "custom",
                                "title": "🎁 Custom Hampers"
                            },
                            {
                                "id": "team",
                                "title": "👨‍💼 Talk to Team"
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

    if request.method == "POST":

        data = request.get_json(force=True)

        try:

            value = data["entry"][0]["changes"][0]["value"]

            if "messages" not in value:
                return "EVENT_RECEIVED", 200

            message = value["messages"][0]
            phone = message["from"]

            # LIST SELECTION

            if message["type"] == "interactive":

                selection = message["interactive"]["list_reply"]["title"]

                user_state[phone] = "waiting_for_requirements"

                user_data[phone] = {
                    "category": selection
                }

                send_text(
                    phone,
                    f"""🌸 {selection}

Please share your requirements.

You can simply type:

• Quantity
• Budget
• Date required
• Delivery location

Example:

Need 50 hampers
Budget ₹2000 each
Delivery in Delhi
Required by 20 June"""
                )

            elif message["type"] == "text":

                text = message["text"]["body"].strip()

                state = user_state.get(phone)

                if state == "waiting_for_requirements":

                    category = user_data[phone]["category"]

                    send_text(
                        phone,
                        f"""✅ Thank you.

Our team has received your enquiry.

Category:
{category}

Summary:

{text}

Our team will contact you shortly."""
                    )

                    print("NEW LEAD")
                    print("Phone:", phone)
                    print("Category:", category)
                    print("Requirement:", text)

                    user_state.pop(phone, None)
                    user_data.pop(phone, None)

                else:

                    send_main_menu(phone)

        except Exception as e:
            print("ERROR:", e)

        return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
```
