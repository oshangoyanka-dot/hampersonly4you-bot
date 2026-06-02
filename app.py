from flask import Flask, request
import os

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "hampers123")

@app.route("/")
def home():
    return "HampersOnly4You Bot Running"

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    print("MODE:", mode)
    print("TOKEN:", token)
    print("VERIFY_TOKEN:", VERIFY_TOKEN)

    if token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)