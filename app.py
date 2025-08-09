from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from openai import OpenAI
import re
import openpyxl # Library for Excel
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app) # For development, you can keep this open. For production, restrict it.

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Shortcut Replies ---
shortcuts = {
    "price": "Our basic plan starts at ₹299/month.",
    "timing": "We're open from 10 AM to 8 PM every day.",
    "location": "We’re located near Gachibowli, Hyderabad.",
    "services": "We offer grooming, styling, and facial treatments.",
    "whatsapp": "Please message us at +91-90000-00000.",
    "ritesh": "Ritesh is our best employee!",
    "navin": "Navin is our CEO"
}

# --- Keywords to trigger the contact form ---
CONTACT_TRIGGERS = ["contact", "talk to you", "speak to you", "leave my details", "connect"]

# --- Function to save leads to an Excel file ---
def save_lead_to_excel(name, email):
    filename = "leads.xlsx"
    # Define the headers
    headers = ["Timestamp", "Name", "Email"]

    # Check if the file exists
    if not os.path.exists(filename):
        # Create a new workbook and select the active sheet
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Leads"
        # Append the headers
        sheet.append(headers)
        print(f"Created new Excel file: {filename}")
    else:
        # Load the existing workbook
        workbook = openpyxl.load_workbook(filename)
        sheet = workbook.active

    # Append the new lead data
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append([timestamp, name, email])

    # Save the workbook
    workbook.save(filename)
    print(f"Successfully saved lead: {name}, {email}")


# --- Main Chat Route ---
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "").lower()

    # 1. Check for simple keyword shortcuts first
    for keyword, reply in shortcuts.items():
        if keyword in message:
            return jsonify({"reply": reply})

    # 2. Check if the message triggers the contact form
    for trigger in CONTACT_TRIGGERS:
        if trigger in message:
            # Send a special response to the frontend to show the form
            return jsonify({
                "reply": "We just need some more information from you to proceed.",
                "action": "collect_lead" # Special action key
            })

    # 3. Fallback to OpenAI if no trigger is found
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a friendly and helpful AI assistant named Pixelite. Keep your answers concise."},
                {"role": "user", "content": message}
            ],
            max_tokens=150,
            temperature=0.7
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return jsonify({"reply": "Sorry, I'm having a bit of trouble connecting right now. Please try again later."}), 500

# --- New Route to Handle Lead Collection ---
@app.route("/collect-lead", methods=["POST"])
def collect_lead():
    data = request.json
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"status": "error", "message": "Name and email are required."}), 400

    try:
        save_lead_to_excel(name, email)
        return jsonify({"status": "success", "message": "Lead captured successfully!"})
    except Exception as e:
        print(f"Excel Error: {e}")
        return jsonify({"status": "error", "message": "Could not save lead."}), 500


if __name__ == "__main__":
    # Use debug=False for production
    app.run(debug=True)
