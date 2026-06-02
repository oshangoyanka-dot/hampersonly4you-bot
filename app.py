from flask import Flask, request
import os
import requests

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")

PHONE_NUMBER_ID = "1135928302934605"

users = {}


def send_text(to, text):

    url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }

    requests.post(url, headers=headers, json=payload)


def send_occasion_menu(to):

    url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"

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
                "text": "👋 Welcome to HampersOnly4You\n\nChoose an Occasion"
            },
            "action": {
                "button": "View Options",
                "sections": [
                    {
                        "title": "Occasions",
                        "rows": [
                            {"id": "birthday", "title": "🎂 Birthday"},
                            {"id": "anniversary", "title": "❤️ Anniversary"},
                            {"id": "wedding", "title": "💍 Wedding"},
                            {"id": "corporate", "title": "🏢 Corporate Gifts"},
                            {"id": "custom", "title": "🎁 Custom Hamper"}
                        ]
                    }
                ]
            }
        }
    }

    requests.post(url, headers=headers, json=payload)


def send_budget_menu(to):

    url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"

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
                            {"id": "b1", "title": "Under ₹1000"},
                            {"id": "b2", "title": "₹1000 - ₹3000"},
                            {"id": "b3", "title": "₹3000 - ₹5000"},
                            {"id": "b4", "title": "₹5000+"}
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
                return "OK", 200

            message = value["messages"][0]
            sender = message["from"]

            if sender not in users:

                users[sender] = {"step": "occasion"}

                send_occasion_menu(sender)

                return "OK", 200

            user = users[sender]

            if message["type"] == "interactive":

                selection = message["interactive"]["list_reply"]["id"]

                if user["step"] == "occasion":

                    user["occasion"] = selection
                    user["step"] = "budget"

                    send_budget_menu(sender)

                    return "OK", 200

                elif user["step"] == "budget":

                    user["budget"] = selection
                    user["step"] = "name"

                    send_text(sender, "Please enter your name.")

                    return "OK", 200

            if message["type"] == "text":

                text = message["text"]["body"]

                if user["step"] == "name":

                    user["name"] = text
                    user["step"] = "address"

                    send_text(sender, "Please enter your address.")

                elif user["step"] == "address":

                    user["address"] = text
                    user["step"] = "quantity"

                    send_text(sender, "Please enter quantity required.")

                elif user["step"] == "quantity":

                    user["quantity"] = text
                    user["step"] = "date"

                    send_text(sender, "Please enter date of requirement.")

                elif user["step"] == "date":

                    user["date"] = text
                    user["step"] = "location"

                    send_text(sender, "Please enter delivery location.")

                elif user["step"] == "location":

                    user["location"] = text

                    summary = f"""
✅ Thank you.

Our team will contact you shortly.

Lead Summary

Occasion: {user['occasion']}
Budget: {user['budget']}
Name: {user['name']}
Address: {user['address']}
Quantity: {user['quantity']}
Date of Requirement: {user['date']}
Location: {user['location']}
"""

                    send_text(sender, summary)

                    print("NEW LEAD:", user)

                    del users[sender]

        except Exception as e:

            print("ERROR:", e, flush=True)

        return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))