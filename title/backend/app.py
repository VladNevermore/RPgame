from flask import Flask, request, jsonify, send_from_directory
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="../frontend/static")

FOLDER_ID = os.getenv("FOLDER_ID")
API_KEY = os.getenv("API_KEY")
YANDEX_MODEL_URI = os.getenv("YANDEX_MODEL_URI")
COMPLETION_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

def generate_summary(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {API_KEY}"
    }
    try:
        response = requests.post(COMPLETION_URL, headers=headers, json=prompt)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    
    print(f"Yandex GPT Response: {response.status_code}, {response.text}")
    return response.json()

@app.route('/api/generate_scenario', methods=['POST'])
def generate_scenario():
    data = request.json
    selected_words = data['words']
    print(f"Received words: {selected_words}")
    prompt = {
        "modelUri": YANDEX_MODEL_URI,
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": 500
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты талантливый сценарист, который создает захватывающие игровые сценарии для браузерных игр."
            },
            {
                "role": "user",
                "text": f"Создай короткий сценарий для игры на основе следующих слов: {', '.join(selected_words)}. Включи конкретную задачу для пользователя. Сценарий должен быть кратким, не более 200 слов, и должен содержать конкретные задачи для игрока."
            }
        ]
    }
    result = generate_summary(prompt)
    if result is None:
        return jsonify({"scenario": "Ошибка в генерации сценария."}), 500
    scenario_text = result.get("result", {}).get("alternatives", [{}])[0].get("message", {}).get("text", "Ошибка в генерации сценария.")
    
    print(f"Generated scenario: {scenario_text}")
    return jsonify({"scenario": scenario_text})

@app.route('/api/process_actions', methods=['POST'])
def process_actions():
    data = request.json
    user_scenario = data['scenario']
    user_actions = data['actions']
    print(f"Received scenario: {user_scenario}")
    print(f"Received actions: {user_actions}")

    prompt = {
        "modelUri": YANDEX_MODEL_URI,
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": 500
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты ассистент дроид, способный помочь в галактических приключениях."
            },
            {
                "role": "user",
                "text": f"Сценарий: {user_scenario}"
            },
            {
                "role": "user",
                "text": f"Действия пользователя: {user_actions}"
            },
            {
                "role": "system",
                "text": "Проанализируй действия пользователя в контексте данного сценария и опиши, к чему они привели. Оцени правильность действий, добавь немного юмора и абсурда. Не включай в текст указания на генерацию или ответственность нейросети."
            }
        ]
    }

    result = generate_summary(prompt)
    if result is None:
        return jsonify({"response": "Ошибка в ответе нейросети."}), 500
    response_text = result.get("result", {}).get("alternatives", [{}])[0].get("message", {}).get("text", "Ошибка в ответе нейросети.")
    
    print(f"Generated response: {response_text}")
    return jsonify({"response": response_text})

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
