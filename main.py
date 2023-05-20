import json
import telebot
import time
import os
from datetime import datetime, timedelta
import random

# инициализируем бота с токеном
bot = telebot.TeleBot("5995350835:AAFzZ9Os5oWSTBCVbuDcnTFAPFULi3V1trA")

# проверяем наличие файла базы данных
if not os.path.exists('C:\\Users\\Venthell\\Desktop\\ChertilaRoulette\\data.json'):
    # если файл не существует, то создаем новую пустую базу данных
    data = {'users': {}}
    save_data(data)

# функция для загрузки данных из базы данных JSON
def load_data():
    with open('C:\\Users\\Venthell\\Desktop\\ChertilaRoulette\\data.json', 'r') as f:
        return json.load(f)

# функция для сохранения данных в базу данных JSON
def save_data(data):
    with open('C:\\Users\\Venthell\\Desktop\\ChertilaRoulette\\data.json', 'w') as f:
        json.dump(data, f, indent=4)

# команда /start для регистрации пользователя и начисления баланса
@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    data = load_data()
    if str(user_id) not in data['users']:
        data['users'][str(user_id)] = {'balance': 1000, 'last_bonus': None}
        save_data(data)
        bot.reply_to(message, "Добро пожаловать!\nВы получили 1000 монет на свой баланс.")
    else:
        bot.reply_to(message, "Вы уже зарегистрированы.\nВаш текущий баланс: " + str(data['users'][str(user_id)]['balance']) + " монет.")

# команда /balance для проверки баланса
@bot.message_handler(commands=['balance'])
def balance_handler(message):
    user_id = message.from_user.id
    data = load_data()
    if str(user_id) in data['users']:
        bot.reply_to(message, "Ваш текущий баланс: " + str(data['users'][str(user_id)]['balance']) + " монет.")
    else:
        bot.reply_to(message, "Вы не зарегистрированы.\nВведите команду /start, чтобы зарегистрироваться.")

# команда /help для получения справки
@bot.message_handler(commands=['help'])
def help_handler(message):
    bot.reply_to(message, "Список доступных команд:\n\n\n/start - зарегистрироваться и получить 1000 монет на баланс\n\n/balance - проверить текущий баланс\n\n/bonus - получить ежедневный бонус\n\n/roulette <цвет> <ставка> - поставить монеты на цвет (красный, черный или зеленый) в рулетке")

# команда /bonus для получения ежедневного бонуса
@bot.message_handler(commands=['bonus'])
def bonus_handler(message):
    user_id = message.from_user.id
    data = load_data()
    if str(user_id) in data['users']:
        last_bonus = data['users'][str(user_id)]['last_bonus']
        if last_bonus is not None and datetime.now() - datetime.strptime(last_bonus, '%Y-%m-%d %H:%M:%S.%f') < timedelta(hours=24):
            remaining_time = datetime.strptime(last_bonus, '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=24) - datetime.now()
            hours = remaining_time.seconds // 3600
            minutes = (remaining_time.seconds // 60) % 60
            bot.reply_to(message, "Ваш ежедневный бонус уже получен.\nСледующий будет доступен через " + str(hours) + " часов " + str(minutes) + " минут.")
        else:
            data['users'][str(user_id)]['balance'] += 100
            data['users'][str(user_id)]['last_bonus'] = str(datetime.now())
            save_data(data)
            bot.reply_to(message, "Вы получили ежедневный бонус в размере 100 монет.\nВаш текущий баланс: " + str(data['users'][str(user_id)]['balance']) + " монет.")
    else:
        bot.reply_to(message, "Вы не зарегистрированы.\nВведите команду /start, чтобы зарегистрироваться.")

@bot.message_handler(commands=['roulette'])
def roulette_handler(message):
    user_id = message.from_user.id
    data = load_data()
    if str(user_id) in data['users']:
        args = message.text.split()[1:]
        if len(args) != 2:
            bot.reply_to(message, "Неверный формат команды.\nИспользуйте: /roulette <color> <amount>")
            return

        color = args[0].lower()
        amount = args[1]

        if color not in ['красный', 'черный', 'зеленый']:
            bot.reply_to(message, "Неверный цвет. Доступные цвета: красный, черный, зеленый")
            return

        try:
            amount = int(amount)
        except ValueError:
            bot.reply_to(message, "Неверное количество монет. Укажите целое число.")
            return

        if amount <= 0:
            bot.reply_to(message, "Неверное количество монет. Укажите положительное число.")
            return

        if amount > data['users'][str(user_id)]['balance']:
            bot.reply_to(message, "У вас недостаточно монет на балансе.")
            return

        # списываем с баланса пользователя сумму ставки
        data['users'][str(user_id)]['balance'] -= amount
        save_data(data)

        # Send the spinning roulette wheel animation
        with open('C:\\Users\\Venthell\\Desktop\\ChertilaRoulette\\gif\\casino-gamble.gif', 'rb') as f:
            bot.send_animation(message.chat.id, f)

        time.sleep(3)  # Delay for 3 seconds to simulate spinning time

        # выполняем случайную генерацию цвета
        result_color = random.choice(['🔴 красный', '⚫ черный', '🟢 зеленый'])

        if result_color.startswith('🔴') and color == 'красный':
            # пользователь выиграл
            win_amount = amount * 2  # выигрыш равен удвоенной сумме ставки
            data['users'][str(user_id)]['balance'] += win_amount
            save_data(data)
            bot.reply_to(message, f"Найс кок! Выпал цвет {result_color}.\nВы получаете {win_amount} монет.\nВаш текущий баланс: {data['users'][str(user_id)]['balance']} монет.")
        elif result_color.startswith('⚫') and color == 'черный':
            # пользователь выиграл
            win_amount = amount * 2  # выигрыш равен удвоенной сумме ставки
            data['users'][str(user_id)]['balance'] += win_amount
            save_data(data)
            bot.reply_to(message, f"СЮДАААААА! Выпал цвет {result_color}.\nВы получаете {win_amount} монет.\nВаш текущий баланс: {data['users'][str(user_id)]['balance']} монет.")
        elif result_color.startswith('🟢') and color == 'зеленый':
            # пользователь выиграл
            win_amount = amount * 14  # выигрыш равен 14-кратной сумме ставки
            data['users'][str(user_id)]['balance'] += win_amount
            save_data(data)
            bot.reply_to(message, f"Имба! Выпал цвет {result_color}.\nВы получаете {win_amount} монет.\nВаш текущий баланс: {data['users'][str(user_id)]['balance']} монет.")
        else:
            # пользователь проиграл
            bot.reply_to(message, f"Ёбаный рот этого казино блять! Выпал цвет {result_color}.\nВы потеряли {amount} монет.\nВаш текущий баланс: {data['users'][str(user_id)]['balance']} монет.")
            save_data(data)

    else:
        bot.reply_to(message, "Вы не зарегистрированы.\nВведите команду /start, чтобы зарегистрироваться.")

# запускаем бота
bot.polling()