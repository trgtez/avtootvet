import telebot
from flask import Flask, request
import threading
import time
import os  # Для чтения переменной окружения
import logging  # Для логирования

# Настроим логирование
logging.basicConfig(level=logging.INFO)  # Уровень логирования — INFO

TOKEN = '8212647592:AAGjpHDjphZSLVZRVwhe1duYvgQ13mUdjtI'  # Используй свой токен
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Словарь для хранения состояния пользователей
user_states = {}

# Ответ на текстовые сообщения
@bot.message_handler(func=lambda msg: True, content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id

    logging.info(f"Received message: {message.text} from {user_id}")

    # Проверяем, если пользователь уже получил ответ, не отвечаем снова
    if user_states.get(user_id) in ['waiting_for_media', 'done', 'finished']:
        return

    # Устанавливаем состояние пользователя как 'waiting_for_media', чтобы он не получал ответ повторно
    user_states[user_id] = 'waiting_for_media'

    # Приветственное сообщение с инструкциями
    bot.reply_to(message, 'Привет! Я автоответчик. Вот что я могу тебе предложить:\n\n'
                           '1️⃣ Лайкни и напиши "спасибо" под комментарием с моим ником в тиктоке!\n'
                           '2️⃣ Напиши под 10 любых видео текст:\n\n'
                           '"хз, всем по подарку подарю @locer2 😉"\n\n'
                           'Когда сделаешь, скинь скрины, и я пришлю подарок!')

    # Запуск отправки дополнительного задания через 7 секунд
    threading.Thread(target=send_task, args=(message,)).start()

# Логика для выполнения задачи через 7 секунд после ответа
def send_task(message):
    time.sleep(7)  # Задержка 7 секунд
    bot.send_message(
        message.chat.id,
        '<strong>1️⃣ Лайкни и напиши "спасибо" под комментарием с моим ником в тиктоке!</strong>\n'
        '(Там где ты увидел комент со мной)\n\n'
        '<strong>2️⃣ Напиши под 10 любых видео этот текст👇</strong>\n\n'
        '<code>хз, всем по подарку подарю @locer2 😉</code>\n\n'
        'ОБЯЗАТЕЛЬНО ЛАЙКАТЬ СВОИ КОММЕНТЫ❗️\n\n'
        'Когда будет готово не забудь скинуть скрины!!!\n\n'
        '️❗️БЕЗ СКРИНОВ НЕ СКИНУ ПОДАРОК❗️\n\n'
        'Больше заданий не будет, после выполнения сразу скину подарок',
        parse_mode='html'
    )

# Ответ на медиа (фото/видео)
@bot.message_handler(content_types=['photo', 'video'])
def handle_media(message):
    user_id = message.from_user.id

    logging.info(f"Received media from {user_id}")

    # Если пользователь уже получил ответ, не отвечаем снова
    if user_states.get(user_id) in ['waiting_for_media', 'done', 'finished']:
        return

    # Устанавливаем состояние пользователя как 'done', чтобы он не получал ответ повторно
    user_states[user_id] = 'done'

    # Ответ на медиа
    bot.send_message(
        message.chat.id,
        'Спасибо за скрины! ❤️\n\n'
        'Теперь проверяю твои комментарии. Пожалуйста, подожди немного.'
    )

    # Запускаем отложенную задачу для отправки подарка через 15 минут
    threading.Thread(target=delayed_gift_message, args=(message.chat.id, user_id)).start()

# Отправка подарка через 15 минут
def delayed_gift_message(chat_id, user_id):
    time.sleep(900)  # 15 минут = 900 секунд
    bot.send_message(chat_id, 'Подарок от меня в этом боте.')
    user_states[user_id] = 'finished'

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    try:
        json_str = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_str)
        logging.info(f"Received update: {update}")  # Логируем входящее сообщение
        bot.process_new_updates([update])
        logging.info(f"Processed update successfully.")  # Логируем успешную обработку
        return 'ok', 200
    except Exception as e:
        logging.error(f"Error while processing update: {e}")  # Логируем ошибки
        return 'Error', 500

@app.route('/')
def index():
    return "Бот работает!", 200

if __name__ == '__main__':
    # Запускаем Flask с нужным хостом и портом из окружения
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
