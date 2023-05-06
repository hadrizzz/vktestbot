import threading
import time
import telebot
import json
from CONST import *


bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
commands = ['/help', '/set', '/get', '/del']


def delete_set_messages(chat_id, message_id):
    time.sleep(PASSWORD_LIFE_TIME_IN_SECONDS)
    bot.delete_message(chat_id, message_id)


# Функция для очистки паролей у пользователя через определенное время
def clean_user_data(chat_id, message_id):
    time.sleep(PASSWORD_LIFE_TIME_IN_SECONDS)
    bot.delete_message(chat_id, message_id)


# Команда /start
@bot.message_handler(commands=['start'])
def start_handler(message):
    """
    Создает для пользователя свой файл на основе chat_id и приветствует его.

    :param message: объект сообщения в Telegram
    :return: None
    """
    # Добавляем пользователя в словарь пользователей
    chat_id = message.chat.id
    temp = open(f'user_data/{chat_id}.txt', 'w+')
    temp.close()
    bot.send_message(chat_id, GREETING)


# Команда /help
@bot.message_handler(commands=['help'])
def help_handler(message):
    """
    Отправляет пользователю сообщение с инструкцией по использованию бота.

    :param message: объект сообщения в Telegram вида: /help
    :return: None
    """
    chat_id = message.chat.id
    bot.send_message(chat_id, HELP_TEXT.format(PASSWORD_LIFE_TIME_IN_SECONDS))


# Команда /set
@bot.message_handler(commands=['set'])
def set_handler(message):
    """
    Добавляет логин и пароль к сервису, сохраняя их в файле для пользователя.

    :param message: Сообщение от пользователя в Telegram вида: /set service login password
    :bot return: Сообщение вида: Логин и пароль для сервиса service успешно сохранены.
    :return: None
    """
    chat_id = message.chat.id
    message_id = message.message_id
    user_data = open(f'user_data/{chat_id}.txt', 'a')
    try:
        _, service, login, password = message.text.split()
    except ValueError:
        bot.send_message(chat_id, INCORRECT_SET.format(commands[1]))
        return
    user_data.write('{"'+service+'": {"login": "'+login+'", "password": "'+password+'"}}\n')
    bot.send_message(chat_id, SUCCESS_SET.format(service))

    # Запускаем отдельный поток для очистки паролей через определенное время
    threading.Thread(target=delete_set_messages, args=(chat_id, message_id)).start()
    user_data.close()


# Команда /get
@bot.message_handler(commands=['get'])
def get_handler(message):
    """
    Получает из файла объект типа JSON, из объекта получает логин и пароль, затем, отправляет их пользователю

    :param message: сообщение от пользователя Telegram вида: /get service
    :bot return: Сообщение вида: Логин и пароль для сервиса service:
                                 Логин: login
                                 Пароль: password
    :return: None
    """
    flag = False
    chat_id = message.chat.id
    user_data = open(f'user_data/{chat_id}.txt', 'r')
    try:
        _, service = message.text.split()
    except ValueError:
        bot.send_message(chat_id, INCORRECT_GET.format(commands[2]))
        return
    for line in user_data:
        if service in line:
            flag = True
            line = json.loads(line)
            login = line[service]["login"]
            password = line[service]["password"]
            break
    if flag:
        bot.send_message(chat_id, SUCCESS_GET.format(service, login, password, PASSWORD_LIFE_TIME_IN_SECONDS))
        message_id = message.message_id + 1
        # Запускаем отдельный поток для очистки паролей через определенное время
        threading.Thread(target=delete_set_messages, args=(chat_id, message_id)).start()
    else:
        bot.send_message(chat_id, FAIL_GET.format(service))
    user_data.close()


# Команда /del
@bot.message_handler(commands=['del'])
def del_handler(message):
    """
    Удаляет из файла строку по сервису

    :param message: сообщение от пользователя Telegram вида: /del service
    :bot return: Сообщение вида: Логин и пароль для сервиса service успешно удалены.
    :return: None
    """
    chat_id = message.chat.id
    user_data = open(f'user_data/{chat_id}.txt', 'r')
    try:
        _, service = message.text.split()
    except ValueError:
        bot.send_message(chat_id, INCORRECT_DEL.format(commands[3]))
        return
    if service in user_data.read():
        user_data.close()
        user_data = open(f'user_data/{chat_id}.txt')
        for line in user_data:
            if service in line:
                a = line
                print(a)
                break
        user_data = open(f'user_data/{chat_id}.txt').read()
        user_data = user_data.replace(a, '')
        temp = open(f'user_data/{chat_id}.txt', 'w').write(user_data)
        bot.send_message(chat_id, SUCCESS_DEL.format(service))
    else:
        bot.send_message(chat_id, FAIL_DEL.format(service))


bot.polling()
