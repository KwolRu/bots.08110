import telebot
import json
from telebot import types

# Создаем экземпляр бота
bot = telebot.TeleBot('6729590441:AAFbHY46fV9LcqmmCMs_ARrr-dzn_AIxNJE')

# Путь к файлу для сохранения заявок
FILE_PATH = 'requests.json'

# Словарь для хранения заявок
requests = {}

# Загрузка заявок из файла при запуске бота
def load_requests():
    global requests
    try:
        with open(FILE_PATH, 'r') as file:
            requests = json.load(file)
    except FileNotFoundError:
        requests = {}

# Сохранение заявок в файл
def save_requests():
    with open(FILE_PATH, 'w') as file:
        json.dump(requests, file)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    # Загружаем заявки из файла
    load_requests()

    # Создаем клавиатуру для выбора действий
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button = types.KeyboardButton(text="Отправить заявку")
    keyboard.add(button)
    button = types.KeyboardButton(text="Просмотреть заявки")
    keyboard.add(button)

    # Отправляем приветственное сообщение с клавиатурой
    bot.send_message(message.chat.id, "Добро пожаловать! Чем могу помочь?", reply_markup=keyboard)

# Обработчик команды "Отправить заявку"
@bot.message_handler(func=lambda message: message.text == "Отправить заявку")
def send_request(message):
    # Запрашиваем у пользователя информацию для заявки
    bot.send_message(message.chat.id, "Введите ваше имя:")
    bot.register_next_step_handler(message, process_name_step)

def process_name_step(message):
    # Генерируем уникальный ID для заявки
    request_id = len(requests) + 1
    # Сохраняем имя пользователя, ID заявки и идентификатор чата
    name = message.text
    chat_id = message.chat.id
    requests[request_id] = {'name': name, 'chat_id': chat_id}
    # Запрашиваем номер телефона
    bot.send_message(chat_id, "Введите ваш номер телефона:")
    bot.register_next_step_handler(message, process_phone_step, request_id)

def process_phone_step(message, request_id):
    # Сохраняем номер телефона
    phone = message.text
    requests[request_id]['phone'] = phone
    # Запрашиваем город
    bot.send_message(message.chat.id, "Введите ваш город:")
    bot.register_next_step_handler(message, process_city_step, request_id)

def process_city_step(message, request_id):
    # Сохраняем город
    city = message.text
    requests[request_id]['city'] = city
    # Запрашиваем описание проблемы
    bot.send_message(message.chat.id, "Введите описание проблемы:")
    bot.register_next_step_handler(message, process_description_step, request_id)

def process_description_step(message, request_id):
    # Сохраняем описание проблемы
    description = message.text
    requests[request_id]['description'] = description
    # Отправляем заявку в определенный канал
    bot.send_message('-4174325026', f"Новая заявка:\nID: {request_id}\nИмя: {requests[request_id]['name']}\nНомер телефона: {requests[request_id]['phone']}\nГород: {requests[request_id]['city']}\nОписание проблемы: {requests[request_id]['description']}")
    # Отправляем пользователю подтверждение с ID заявки
    bot.send_message(message.chat.id, f"Ваша заявка отправлена! ID заявки: {request_id}")

# Обработчик команды "Просмотреть заявки"
@bot.message_handler(func=lambda message: message.text == "Просмотреть заявки")
def view_requests(message):
    # Проверяем, есть ли заявки
    if len(requests) > 0:
        # Формируем список заявок
        requests_list = []
        for request_id, request_data in requests.items():
            request_info = f"ID: {request_id}\nИмя: {request_data['name']}\nНомер телефона: {request_data['phone']}\nГород: {request_data['city']}\nОписание проблемы: {request_data['description']}"
            requests_list.append(request_info)
        # Отправляем список заявок пользователю
        bot.send_message(message.chat.id, "\n\n".join(requests_list))
    else:
        bot.send_message(message.chat.id, "Нет активных заявок")

# Обработчик команды "/answer"
@bot.message_handler(commands=['answer'])
def answer_request(message):
    # Проверяем, указан ли номер заявки
    if len(message.text.split()) > 1:
        request_id = int(message.text.split()[1])
        # Проверяем, существует ли заявка с указанным ID
        if request_id in requests:
            # Запрашиваем текст ответа
            bot.send_message(message.chat.id, "Введите текст ответа:")
            bot.register_next_step_handler(message, process_response_step, request_id)
        else:
            bot.send_message(message.chat.id, "Заявка с указанным ID не найдена")
    else:
        bot.send_message(message.chat.id, "Некорректный формат команды. Используйте /answer <номер_заявки>")

def process_response_step(message, request_id):
    # Сохраняем текст ответа
    response = message.text
    # Отправляем ответ пользователю
    chat_id = requests[request_id]['chat_id']
    bot.send_message(chat_id, f"Ответ на вашу заявку {request_id}:\n{response}")
    # Отправляем ответ в определенный канал
    bot.send_message('-4174325026', f"Ответ на заявку {request_id}:\n{response}")
    # Отправляем пользователю подтверждение
    bot.send_message(message.chat.id, f"Ответ на заявку {request_id} отправлен:\n{response}")

# Сохраняем заявки в файл при остановке бота
@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def save_requests_on_stop(call):
    save_requests()
    bot.send_message(call.message.chat.id, "Бот остановлен. Заявки сохранены.")

# Запускаем бота
try:
    bot.polling()
except KeyboardInterrupt:
    # Сохраняем заявки в файл при принудительной остановке бота
    save_requests()