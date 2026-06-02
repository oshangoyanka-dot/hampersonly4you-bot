from flask import Flask, request
import os
import requests

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")

PHONE_NUMBER_ID = "1135928302934605"

# Temporary storage
users = {}


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
            message = data["entry"][0]["changes"][0]["value"]["messages"][0]
            sender = message["from"]
            text = message["text"]["body"].strip()

            if sender not in users:

                users[sender] = {
                    "step": "occasion"
                }

                send_message(
                    sender,
                    "👋 Welcome to HampersOnly4You\n\n"
                    "Please choose an occasion:\n\n"
                    "1️⃣ Birthday\n"
                    "2️⃣ Anniversary\n"
                    "3️⃣ Wedding\n"
                    "4️⃣ Corporate Gifts\n"
                    "5️⃣ Custom Hamper"
                )

                return "EVENT_RECEIVED", 200

            user = users[sender]

            # Occasion
            if user["step"] == "occasion":

                occasions = {
                    "1": "Birthday",
                    "2": "Anniversary",
                    "3": "Wedding",
                    "4": "Corporate Gifts",
                    "5": "Custom Hamper"
                }

                user["occasion"] = occasions.get(text, text)
                user["step"] = "budget"

                send_message(
                    sender,
                    f"🎁 Occasion Selected: {user['occasion']}\n\n"
                    "Please choose your budget:\n\n"
                    "1️⃣ Under ₹1000\n"
                    "2️⃣ ₹1000 - ₹3000\n"
                    "3️⃣ ₹3000 - ₹5000\n"
                    "4️⃣ ₹5000+"
                )

            elif user["step"] == "budget":

                budgets = {
                    "1": "Under ₹1000",
                    "2": "₹1000 - ₹3000",
                    "3": "₹3000 - ₹5000",
                    "4": "₹5000+"
                }

                user["budget"] = budgets.get(text, text)
                user["step"] = "name"

                send_message(sender, "Please enter your name.")

            elif user["step"] == "name":

                user["name"] = text
                user["step"] = "address"

                send_message(sender, "Please enter your address.")

            elif user["step"] == "address":

                user["address"] = text
                user["step"] = "quantity"

                send_message(sender, "Please enter quantity required.")

            elif user["step"] == "quantity":

                user["quantity"] = text
                user["step"] = "date"

                send_message(
                    sender,
                    "Please enter date of requirement.\nExample: 15 June 2026"
                )

            elif user["step"] == "date":

                user["date"] = text
                user["step"] = "location"

                send_message(sender, "Please enter delivery location/city.")

            elif user["step"] == "location":

                user["location"] = text

                summary = (
                    "✅ Thank you for your enquiry.\n\n"
                    "Our team will contact you shortly.\n\n"
                    "Lead Summary\n\n"
                    f"Occasion: {user['occasion']}\n"
                    f"Budget: {user['budget']}\n"
                    f"Name: {user['name']}\n"
                    f"Address: {user['address']}\n"
                    f"Quantity: {user['quantity']}\n"
                    f"Date of Requirement: {user['date']}\n"
                    f"Location: {user['location']}"
                )

                send_message(sender, summary)

                print("NEW LEAD:", user, flush=True)

                del users[sender]

        except Exception as e:
            print("ERROR:", e, flush=True)

        return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))