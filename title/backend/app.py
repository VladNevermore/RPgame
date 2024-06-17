from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv("API_KEY")

def generate_summary(prompt):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai.api_key}'
    }
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

@app.route('/api/generate_scenario', methods=['POST'])
def generate_scenario():
    try:
        data = request.json
        words = data['words']
        app.logger.info(f"Received words: {words}")
        prompt = (
            f"Вы играете в игру на выживание. "
            f"Ваши слова: {', '.join(words)}. "
            "Опишите сценарий."
        )
        result = generate_summary(prompt)
        return jsonify({'scenario': result})
    except Exception as e:
        app.logger.error(f"Error generating scenario: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/api/process_actions', methods=['POST'])
def process_actions():
    try:
        data = request.json
        scenario = data['scenario']
        actions = data['actions']
        app.logger.info(f"Received actions: {actions} for scenario: {scenario}")
        prompt = (
            f"Сценарий: {scenario}\n"
            f"Ваши действия: {actions}\n"
            "Опишите результат."
        )
        result = generate_summary(prompt)
        return jsonify({'response': result})
    except Exception as e:
        app.logger.error(f"Error processing actions: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
