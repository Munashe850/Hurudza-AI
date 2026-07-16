from flask import Flask, request
import os

app = Flask(__name__)
VERIFY_TOKEN = "hurudza123"

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    print("Got message:", request.get_json())
    return "ok", 200

@app.route("/", methods=["GET"])
def home():
    return {"status": "Hurudza AI is running"}, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
