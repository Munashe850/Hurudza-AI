import os
import requests
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# GROQ SETUP - FREE
GROQ_API_KEY = os.environ.get("OPENAI_API_KEY") # we reuse the same var name
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY
)

# WHATSAPP SETUP
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        from_number = message["from"]
        msg_body = message["text"]["body"]

        # GET AI REPLY FROM GROQ - FREE
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", # super fast + free
            messages=[
                {"role": "system", "content": "You are Hurudza AI, a helpful farming assistant for Zimbabwe farmers. Reply in short, friendly messages."},
                {"role": "user", "content": msg_body}
            ]
        )
        ai_reply = response.choices[0].message.content

        # SEND REPLY TO WHATSAPP
        url = f"https://graph.facebook.com/v20.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
        payload = {"messaging_product": "whatsapp", "to": from_number, "text": {"body": ai_reply}}
        requests.post(url, headers=headers, json=payload)

    except Exception as e:
        print("Error:", e)

    return jsonify({"status": "ok"}), 200

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Hurudza AI is running"}), 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)