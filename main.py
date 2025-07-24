import telebot
from flask import Flask, request
import threading
import time
import os  # Добавлен импорт для чтения переменной окружения

TOKEN = '8212647592:AAGjpHDjphZSLVZRVwhe1duYvgQ13mUdjtI'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_states = {}

@bot.message_handler(func=lambda msg: True, content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id

    if user_states.get(user_id) in ['waiting_for_media', 'done', 'finished']:
        return

    user_states[user_id] = 'waiting_for_media'

    time.sleep(4)
    bot.reply_to(message, 'Приветик, я могу подарить подарок за 350 ⭐️, осталось всего 48 штучек.\n\nНо есть задание:')
    time.sleep(7)
    bot.send_message(
        message.chat.id,
        '<strong>1️⃣ Лайкни и напиши "спасибо" под комментарием с моим ником в тиктоке!</strong>\n'
        '(Там где ты увидел комент со мной)\n\n'
        '<strong>2️⃣ Напиши под 10 любых видео этот текст👇</strong>\n\n'
        '<code>хз, всем по подарку подарю @locer2 😉</code>\n\n'
        'ОБЯЗАТЕЛЬНО ЛАЙКАТЬ СВОИ КОММЕНТЫ❗️\n\n'
        'Когда будет готово не забудь скинуть скрины!!!\n\n'
        '️❗БЕЗ СКРИНОВ НЕ СКИНУ ПОДАРОК❗️\n\n'
        'Больше заданий не будет, после выполнения сразу скину подарок',
        parse_mode='html'
    )

@bot.message_handler(content_types=['photo', 'video'])
def handle_media(message):
    user_id = message.from_user.id

    if user_states.get(user_id) == 'waiting_for_media':
        user_states[user_id] = 'done'

        time.sleep(7)
        bot.send_message(
            message.chat.id,
            'Спасибо за комменты! ❤️\n\n'
            'Мне надо до 15 минут для того, чтобы проверить твои комментарии! ⏳\n\n'
            'Потому что большая очередь на подарки\n\n'
            'Если ты не сделал 10 комментов, то подарка к сожалению не будет :(\n\n'
            'У тебя есть еще 5 минут если ты не сделал 10 коментов.'
        )

        threading.Thread(target=delayed_gift_message, args=(message.chat.id, user_id)).start()

def delayed_gift_message(chat_id, user_id):
    time.sleep(900)  # 15 минут = 900 секунд
    bot.send_message(chat_id, 'Подарок от меня в этом боте.')
    user_states[user_id] = 'finished'

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'ok', 200

@app.route('/')
def index():
    return "Бот работает!", 200

if __name__ == '__main__':
    # Запускаем Flask с нужным хостом и портом из окружения
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
