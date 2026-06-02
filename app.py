from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "hampers123"

@app.route("/")
def home():
    return "HampersOnly4You Bot Running"

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)