import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ.get('TELEGRAM_TOKEN')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')

TELEGRAM_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'
DEFAULT_MODEL = 'openrouter/free'

WELCOME_MESSAGE = """
👋 Привет! Я **Курсорик** — твой ИИ-помощник.

✨ Я умею:
• Отвечать на любые вопросы
• Генерировать текст и идеи
• Переводить с любого языка
• Помогать с кодом
• Объяснять сложное простым языком

💬 Просто напиши мне что-нибудь, и я отвечу!

🔹 Попробуй: задай вопрос, попроси перевести или написать текст.
"""

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        if data and 'message' in data:
            chat_id = data['message']['chat']['id']
            user_text = data['message'].get('text')
            
            # Обработка команды /start (без статуса)
            if user_text == '/start':
                send_telegram_message(chat_id, WELCOME_MESSAGE)
                return 'ok', 200
            
            if user_text:
                # 1. Сразу отправляем статус "Думаю..."
                send_telegram_message(chat_id, '⏳ Думаю...')
                
                # 2. Получаем ответ от ИИ
                bot_reply = ask_openrouter(user_text)
                
                # 3. Отправляем ответ
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
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
        if response.status_code != 200:
            print(f'Ошибка OpenRouter: {response.status_code}, {response.text}')
            return 'Извините, произошла ошибка при обращении к ИИ. Попробуйте позже.'
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f'Ошибка запроса: {e}')
        return f'Ошибка: {str(e)}'

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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
