import openai
import os
import logging
from flask import Flask, render_template, request, jsonify
from tenacity import retry, stop_after_attempt, wait_fixed

max_attempts = 3
wait_seconds = 2

openai.api_key = os.getenv("OPENAI_API_KEY")
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
ADMIN_PASSWORD = 'M1lf-Me'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_password', methods=['POST'])
def submit_password():
    data = request.get_json()
    password = data['password']

    if validate_password(password):
        return jsonify({'result': 'success'}), 200
    else:
        return jsonify({'result': 'incorrect_password'}), 401

@app.route('/hidden', methods=["GET", "POST"])
def hidden():
    app.logger.debug("hidden route accessed")
    return render_template('hidden.html')

def validate_password(password):
    return password == ADMIN_PASSWORD

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    try:
        response = call_gpt4_api(data["messages"])
        return jsonify(response)
    except Exception as e:
        app.logger.error(f"Error in chat route: {e}")
        return jsonify({"error": "An error occurred while processing your request. Please try again later."}), 500

@retry(stop=stop_after_attempt(max_attempts), wait=wait_fixed(wait_seconds))
def call_gpt4_api(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    return response['choices'][0]['message']['content'].strip()

if __name__ == '__main__':
    app.run(debug=True)


