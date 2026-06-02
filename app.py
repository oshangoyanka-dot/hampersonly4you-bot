from flask import Flask, request
import requests
import os

app = Flask(**name**)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")

PHONE_NUMBER_ID = "1135928302934605"

user_state = {}
user_data = {}

def send_text(phone, text):

```
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
```

def send_occasion_menu(phone):

```
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
```

def send_budget_menu(phone):

```
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
            "text": "Please select your budget per hamper"
        },
        "action": {
            "button": "Select Budget",
            "sections": [
                {
                    "title": "Budget",
                    "rows": [
                        {
                            "id": "budget1",
                            "title": "Under ₹1000"
                        },
                        {
                            "id": "budget2",
                            "title": "₹1000 - ₹3000"
                        },
                        {
                            "id": "budget3",
                            "title": "₹3000 - ₹5000"
                        },
                        {
                            "id": "budget4",
                            "title": "₹5000+"
                        }
                    ]
                }
            ]
        }
    }
}

requests.post(url, headers=headers, json=payload)
```

@app.route("/")
def home():
return "HampersOnly4You Bot Running"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():

```
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

        if message["type"] == "interactive":

            selection = message["interactive"]["list_reply"]["title"]

            state = user_state.get(phone)

            if state == "waiting_for_budget":

                user_data[phone]["budget"] = selection
                user_state[phone] = "waiting_for_details"

                send_text(
                    phone,
                    """🌸 Please share below information:
```

Quantity -
Date of requirement -
Location -
"""
)

```
            else:

                user_data[phone] = {
                    "occasion": selection
                }

                user_state[phone] = "waiting_for_budget"

                send_budget_menu(phone)

        elif message["type"] == "text":

            text = message["text"]["body"].strip()

            state = user_state.get(phone)

            if state == "waiting_for_details":

                occasion = user_data[phone]["occasion"]
                budget = user_data[phone]["budget"]

                send_text(
                    phone,
                    f"""✅ Thank you.
```

Our team will contact you shortly.

Lead Summary

Phone Number - {phone}
Occasion - {occasion}
Budget per hamper - {budget}

{text}
"""
)

```
                print("NEW LEAD")
                print("Phone Number:", phone)
                print("Occasion:", occasion)
                print("Budget:", budget)
                print("Details:", text)

                user_state.pop(phone, None)
                user_data.pop(phone, None)

            else:

                send_occasion_menu(phone)

    except Exception as e:
        print("ERROR:", str(e))

    return "EVENT_RECEIVED", 200
```

if **name** == "**main**":
app.run(
host="0.0.0.0",
port=int(os.environ.get("PORT", 10000)))
