import json
import requests

# Load hotel data from JSON file
with open("hotel_knowledge_base.json", "r") as file:
    hotel_data = json.load(file)

# GROQ API details
GROQ_API_KEY = "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"  # Replace with your actual API key
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

from flask import Flask, request, jsonify, render_template_string


app = Flask(__name__)



# Convert JSON to a string for LLM context
hotel_data_str = json.dumps(hotel_data, indent=2)

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

# Function to query LLM
def query_llm(user_input):
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {"role": "system", "content": f"You are a hotel assistant. Answer only based on the following hotel data: {hotel_data_str}"},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.2  # Lower temperature for factual responses
    }

    response = requests.post(GROQ_ENDPOINT, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Error retrieving response. Status Code: {response.status_code}"}


@app.route("/")
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hotel Chatbot</title>
        <script>
            function sendMessage() {
                let userMessage = document.getElementById("userMessage").value;
                if (userMessage.trim() === "") return;

                let chatBox = document.getElementById("chatBox");
                chatBox.innerHTML += `<p><strong>You:</strong> ${userMessage}</p>`;

                fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: userMessage })
                })
                .then(response => response.json())
                .then(data => {
                    chatBox.innerHTML += `<p><strong>Bot:</strong> ${data.response}</p>`;
                });

                document.getElementById("userMessage").value = "";  // Clear input
            }
        </script>
    </head>
    <body>
        <h1>Hotel Booking Chatbot</h1>
        <div id="chatBox" style="border: 1px solid #ccc; padding: 10px; height: 300px; overflow-y: scroll;"></div>
        <input type="text" id="userMessage" placeholder="Ask about rooms...">
        <button onclick="sendMessage()">Send</button>
    </body>
    </html>
    """)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    if not user_input:
        return jsonify({"response": "Invalid input."})

    response = query_llm(user_input)
    
    bot_reply = response.get("choices", [{}])[0].get("message", {}).get("content", "Error in response")
    
    # Convert bot response into formatted HTML
    formatted_response = bot_reply.replace("\n", "<br>")  # Newline to HTML line break

    return jsonify({"response": formatted_response})

if __name__ == "__main__":
    app.run(debug=True)
