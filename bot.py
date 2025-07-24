import telebot
from flask import Flask, request

TOKEN = '8212647592:AAGjpHDjphZSLVZRVwhe1duYvgQ13mUdjtI'  # Заменить на реальный
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Обработка входящих сообщений
@bot.message_handler(content_types=['text'])
def handle_text(message):
    bot.send_message(message.chat.id, "Привет! Это бот через Webhook 😊")

# Входящий Webhook
@app.route(f'/{TOKEN}', methods=['POST'])
def receive_update():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'ok', 200

# Проверка сервера
@app.route('/', methods=['GET'])
def index():
    return 'Бот работает!', 200
