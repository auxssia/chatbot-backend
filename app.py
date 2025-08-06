from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Shortcut replies
shortcuts = {
    "price": "Our basic plan starts at ₹299/month.",
    "timing": "We're open from 10 AM to 8 PM every day.",
    "location": "We’re located near Gachibowli, Hyderabad.",
    "services": "We offer grooming, styling, and facial treatments.",
    "whatsapp": "Please message us at +91-90000-00000.",
    "ritesh": "Ritesh is our best employee!",
    "navin": "Navin is our CEO",
    "pallavi": "Pallavi is the best psychotherapist in Vijayawada.",
    "vaishu": "Vaishu is a monkey",
    "ramana": "Ramana is a professional stock trader in Vijayawada"
}

# Serve chatbot UI
@app.route("/")
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Pixelite AI</title>
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: 'Segoe UI', sans-serif;
      background-image: url('https://i.ibb.co/39VR3TH1/fixed-background.png');
      background-size: cover;
      background-repeat: no-repeat;
      background-position: center;
      height: 100vh;
      display: flex;
      justify-content: flex-end;
      align-items: flex-end;
      padding: 20px;
    }

    #popup-container {
      position: fixed;
      bottom: 20px;
      right: 20px;
    }

    #arrow {
      position: absolute;
      right: 80px;
      bottom: 60px;
      width: 60px;
    }

    #popup-button {
      width: 60px;
      height: 60px;
      cursor: pointer;
      z-index: 1000;
    }

    #chat-container {
      width: 380px;
      height: 75vh;
      border-radius: 24px;
      display: none;
      flex-direction: column;
      overflow: hidden;
      box-shadow: 0 12px 36px rgba(0, 0, 0, 0.3);
      background-color: white;
      position: fixed;
      bottom: 100px;
      right: 20px;
      z-index: 1001;
    }

    #chat-header {
      background-color: #7c3aed;
      color: white;
      font-weight: bold;
      padding: 16px;
      font-size: 18px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    #chat-header::before {
      content: "🤖";
    }

    #chat-messages {
      flex: 1;
      padding: 16px;
      overflow-y: auto;
      background-color: #f9f9f9;
    }

    #chat-input-area {
      display: flex;
      padding: 12px 16px;
      background-color: white;
      gap: 8px;
      border-top: 1px solid #eee;
    }

    #chat-input {
      flex: 1;
      padding: 10px 14px;
      border: 1px solid #ccc;
      border-radius: 20px;
      outline: none;
    }

    #send-button {
      background-color: #7c3aed;
      color: white;
      border: none;
      padding: 10px 18px;
      border-radius: 20px;
      cursor: pointer;
      font-weight: bold;
    }

    #send-button:hover {
      background-color: #5b21b6;
    }
  </style>
</head>
<body>
  <div id="popup-container">
    <img id="arrow" src="https://i.ibb.co/wZLsd2wf/image.png" alt="arrow" />
    <img id="popup-button" src="https://i.ibb.co/27Lm51QL/image.png" alt="popup-button" />
  </div>

  <div id="chat-container">
    <div id="chat-header">Pixelite AI</div>
    <div id="chat-messages"></div>
    <div id="chat-input-area">
      <input type="text" id="chat-input" placeholder="Type your message..." />
      <button id="send-button">Send</button>
    </div>
  </div>

  <script>
    const input = document.getElementById("chat-input");
    const send = document.getElementById("send-button");
    const messages = document.getElementById("chat-messages");
    const popupBtn = document.getElementById("popup-button");
    const chatContainer = document.getElementById("chat-container");

    popupBtn.onclick = () => {
      chatContainer.style.display = chatContainer.style.display === "flex" ? "none" : "flex";
    };

    function appendMessage(role, text) {
      const msg = document.createElement("div");
      msg.textContent = (role === "user" ? "🧑 " : "🤖 ") + text;
      msg.style.margin = "8px 0";
      messages.appendChild(msg);
      messages.scrollTop = messages.scrollHeight;
    }

    async function sendMessage() {
      const text = input.value.trim();
      if (!text) return;
      appendMessage("user", text);
      input.value = "";

      try {
        const res = await fetch("/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text })
        });

        const data = await res.json();
        appendMessage("bot", data.reply || "No reply.");
      } catch (e) {
        appendMessage("bot", "❌ Error contacting server.");
      }
    }

    send.onclick = sendMessage;
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") sendMessage();
    });
  </script>
</body>
</html>
""")

# Health check
@app.route("/health")
def health():
    return "✅ Chatbot backend is live!"

# Main chat route
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "").lower()

    # Keyword shortcut reply
    for keyword in shortcuts:
        if keyword in message:
            return jsonify({"reply": shortcuts[keyword]})

    # OpenAI fallback
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a friendly assistant for a small local business."},
                {"role": "user", "content": message}
            ],
            max_tokens=200,
            temperature=0.7
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({"reply": reply})
    except Exception as e:
        print("Error:", e)
        return jsonify({"reply": "Sorry, I’m having trouble right now. Please try again later."}), 500

if __name__ == "__main__":
    app.run(debug=True)
