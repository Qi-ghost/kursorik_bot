import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Получаем токены из переменных окружения
BOT_TOKEN = os.environ.get('TELEGRAM_TOKEN')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')

# URL для отправки сообщений в Telegram
TELEGRAM_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

# URL API OpenRouter
OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'

# Модель по умолчанию
DEFAULT_MODEL = 'openai/gpt-3.5-turbo'

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        if data and 'message' in data:
            chat_id = data['message']['chat']['id']
            user_text = data['message'].get('text')
            
            if user_text:
                bot_reply = ask_openrouter(user_text)
                send_telegram_message(chat_id, bot_reply)
        
        return 'ok', 200
    except Exception as e:
        print(f'Ошибка в webhook: {e}')
        return 'error', 500

def ask_openrouter(prompt):
    headers = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': DEFAULT_MODEL,
        'messages': [{'role': 'user', 'content': prompt}]
    }
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f'Ошибка OpenRouter: {e}')
        return 'Извините, произошла ошибка. Попробуйте позже.'

def send_telegram_message(chat_id, text):
    payload = {'chat_id': chat_id, 'text': text}
    try:
        requests.post(TELEGRAM_URL, json=payload, timeout=10)
    except Exception as e:
        print(f'Ошибка отправки: {e}')

@app.route('/')
def index():
    return 'Курсорик работает!'

def set_webhook():
    # ВАЖНО: замените kursorik-bot-rkb2 на ваш реальный адрес!
    webhook_url = 'https://kursorik-bot-rkb2.onrender.com/webhook'
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print('Вебхук установлен')
        else:
            print(f'Ошибка: {response.text}')
    except Exception as e:
        print(f'Не удалось установить вебхук: {e}')

if __name__ == '__main__':
    set_webhook()
    # Правильный порт для Render
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
