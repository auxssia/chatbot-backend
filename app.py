from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client once at the top
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Keyword-based quick replies
shortcuts = {
    "price": "Our basic plan starts at ₹299/month.",
    "timing": "We're open from 10 AM to 8 PM every day.",
    "location": "We’re located near Gachibowli, Hyderabad.",
    "services": "We offer grooming, styling, and facial treatments.",
    "whatsapp": "Please message us at +91-90000-00000.",
    "ritesh": "Ritesh is our best employee!"
}

# Health check route
@app.route("/")
def home():
    return "✅ Chatbot backend is live!"

# Main chat route
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '').lower()

    # Check for shortcut replies
    for keyword in shortcuts:
        if keyword in message:
            return jsonify({"reply": shortcuts[keyword]})

    # Fallback to GPT if no shortcut matched
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

if __name__ == '__main__':
    app.run(debug=True)
