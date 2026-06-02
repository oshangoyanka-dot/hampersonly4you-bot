from flask import Flask, request
import os
import requests

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
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=payload)


def send_occasion_menu(phone):
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
            "header": {"type": "text", "text": "👋 Welcome to HampersOnly4You"},
            "body": {"text": "Choose an Occasion"},
            "action": {
                "button": "View Options",
                "sections": [{
                    "title": "Occasions",
                    "rows": [
                        {"id": "birthday", "title": "🎂 Birthday"},
                        {"id": "anniversary", "title": "❤️ Anniversary"},
                        {"id": "wedding", "title": "💍 Wedding"},
                        {"id": "corporate", "title": "🏢 Corporate Gifts"},
                        {"id": "custom", "title": "🎁 Custom Hamper"}
                    ]
                }]
            }
        }
    }

    requests.post(url, headers=headers, json=payload)


def send_budget_menu(phone):
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
            "body": {"text": "Please select your budget per hamper"},
            "action": {
                "button": "Select Budget",
                "sections": [{
                    "title": "Budget",
                    "rows": [
                        {"id": "b1", "title": "Under ₹1000"},
                        {"id": "b2", "title": "₹1000 - ₹3000"},
                        {"id": "b3", "title": "₹3000 - ₹5000"},
                        {"id": "b4", "title": "₹5000+"}
                    ]
                }]
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

    data = request.get_json(force=True)

    try:
        value = data["entry"][0]["changes"][0]["value"]

        if "messages" not in value:
            return "EVENT_RECEIVED", 200

        message = value["messages"][0]
        phone = message["from"]

        if message["type"] == "interactive":
            selection = message["interactive"]["list_reply"]["title"]

            if user_state.get(phone) == "waiting_budget":
                user_data[phone]["budget"] = selection
                user_state[phone] = "waiting_details"

                send_text(
                    phone,
                    "🌸 Please share below information\n\nQuantity -\nDate of requirement -\nLocation -"
                )

            else:
                user_data[phone] = {"occasion": selection}
                user_state[phone] = "waiting_budget"
                send_budget_menu(phone)

        elif message["type"] == "text":
            text = message["text"]["body"].strip()

            if user_state.get(phone) == "waiting_details":
                lines = [x.strip() for x in text.splitlines() if x.strip()]

                quantity = lines[0] if len(lines) > 0 else "Not Provided"
                date_req = lines[1] if len(lines) > 1 else "Not Provided"
                location = lines[2] if len(lines) > 2 else "Not Provided"

                occasion = user_data[phone].get("occasion", "")
                budget = user_data[phone].get("budget", "")

                summary = f"""✅ Thank you.

Our team will contact you shortly.

Lead Summary

Phone Number - {phone}
Occasion - {occasion}
Budget per hamper - {budget}
Quantity - {quantity}
Date of requirement - {date_req}
Location - {location}"""

                send_text(phone, summary)

                user_state.pop(phone, None)
                user_data.pop(phone, None)

            else:
                send_occasion_menu(phone)

    except Exception as e:
        print("ERROR:", str(e))

    return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

def save_to_google_sheet(phone, occasion, budget, quantity, date_req, location):

    webhook = os.getenv("GOOGLE_SHEET_WEBHOOK")

    payload = {
        "phone": phone,
        "occasion": occasion,
        "budget": budget,
        "quantity": quantity,
        "date_required": date_req,
        "location": location
    }

    requests.post(webhook, json=payload)
