import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types
import datetime
from datetime import timedelta
from sqlighter import SQLighter
import exchange_rates
import config

bot = telebot.TeleBot(config.TOKEN)

db = SQLighter('tgbot_db.db')

main_buttons = telebot.types.ReplyKeyboardMarkup(True, True, True)
main_buttons.row('Coronavirus', 'New articles', 'Exchange Rates')

button_sub = telebot.types.ReplyKeyboardMarkup(True)
button_sub.row('Subscribe')


@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.send_message(message.chat.id, f'BOT LAUNCHED\n\n {config.command_list}', reply_markup=button_sub)


@bot.message_handler(commands=['help'])
def cmd_help(message):
    bot.send_message(message.chat.id, config.command_list, reply_markup=button_sub)


def chek(message):
    try:
        if not db.get_subscriptions(status=False):
            now = datetime.datetime.now()
            date = now.strftime('%d-%m-%Y %H:%M')
            if date < db.date_chek(user_id=message.from_user.id):
                return True
            else:
                bot.send_message(message.chat.id,
                                 'Your subscription has expired, you need to click on the "Subscribe" button or enter the command /subscribe',
                                 reply_markup=button_sub)
        else:
            bot.send_message(message.chat.id,
                             'To use this command, you need to click on the "Subscribe" button or enter the command /subscribe',
                             reply_markup=button_sub)
    except TypeError:
        bot.send_message(message.chat.id, 'You are not subscribed')


@bot.message_handler(commands=['subscribe'])
def cmd_subscribe(message):
    now = datetime.datetime.now()
    date = now.strftime('%d-%m-%Y %H:%M')
    if not db.subscriber_exists(message.from_user.id):
        date_to = datetime.datetime.now() + timedelta(days=7)
        sum_date = date_to.strftime('%d-%m-%Y %H:%M')
        db.add_subscriber(user_id=message.from_user.id, status=True, date_from=date, date_to=sum_date)
        bot.send_message(message.chat.id, 'Hurrah! You have successfully subscribed for 7 days',
                         reply_markup=main_buttons)
    elif not db.get_subscriptions(status=False):
        if date > db.date_chek(user_id=message.from_user.id) and not db.get_subscriptions(status=False):
            date_to = datetime.datetime.now() + timedelta(days=7)
            sum_date = date_to.strftime('%d-%m-%Y %H:%M')
            db.update_date(user_id=message.from_user.id, date_to=sum_date)
            bot.send_message(message.chat.id, 'Hurrah! You have successfully renewed your subscription for 7 days',
                             reply_markup=main_buttons)
        else:
            bot.send_message(message.chat.id, 'You are so subscribed')
    elif db.get_subscriptions(False):
        db.update_subscription(message.from_user.id, True)
        bot.send_message(message.chat.id, 'Hurrah! You are subscribed again', reply_markup=main_buttons)


@bot.message_handler(commands=['unsubscribe'])
def cmd_unsubscribe(message):
    if not db.subscriber_exists(message.from_user.id) or db.get_subscriptions(False):
        bot.send_message(message.chat.id, 'You are not subscribed already.')
    else:
        db.update_subscription(message.from_user.id, False)
        bot.send_message(message.chat.id, 'You have successfully unsubscribed.', reply_markup=button_sub)


@bot.message_handler(commands=['addemail'])
def cmd_add_email(message):
    if db.subscriber_exists(message.from_user.id):
        try:
            email = message.text.split()
            db.add_email(user_id=message.from_user.id, email=email[1])
            bot.send_message(message.chat.id, f'Mail {email[1]} successfully linked')
        except IndexError:
            bot.send_message(message.chat.id, 'Enter: /add_email {your mail without brackets}')
    else:
        bot.send_message(message.chat.id,
                         'To use this command you need to click on the "Subscribe" button or enter the command /subscribe',
                         reply_markup=button_sub)


@bot.message_handler(commands=['addate'])
def cmd_add_date(message):
    try:
        if db.subscriber_exists(user_id='your id telegram'):
            date_user = message.text.split()
            last_date = db.date_chek(user_id=int(date_user[1]))
            date_to = datetime.datetime.strptime(last_date, '%d-%m-%Y %H:%M') + timedelta(days=int(date_user[2]))
            sum_date = date_to.strftime('%d-%m-%Y %H:%M')
            db.update_date(user_id=int(date_user[1]), date_to=sum_date)
            bot.send_message(message.chat.id, f'User {date_user[1]} has been renewed for {date_user[2]} days.')
        else:
            bot.send_message(message.chat.id, 'You are not authorized to use this command.')
    except IndexError:
        bot.send_message(message.chat.id, 'Enter: /add_date {user id} {number of days you want to add}')
    except TypeError:
        bot.send_message(message.chat.id, 'There is no such user in the database')


@bot.message_handler(commands=['covid'])
def cmd_covid(message):
    if chek(message):
        response = requests.get('https://yandex.ru/web-maps/covid19?ll=41.775580%2C54.894027&z=3')
        page = response.text
        soup = BeautifulSoup(page, 'html.parser')
        figures = []
        for figures1 in soup.select('div.covid-stat-view__item-value'):
            figures.append(figures1.text)
        bot.send_message(message.chat.id, 'Coronavirus statistics in Russia:\n'
                                          '\n'
                                          f'Confirmed by {figures[0]} people\n'
                                          f'New cases: {figures[1]}\n'
                                          f'Convalescence: {figures[2]}\n'
                                          f'Deaths: {figures[3]}\n', reply_markup=main_buttons)


@bot.message_handler(commands=['news'])
def cmd_news(message):
    if chek(message):
        response = requests.get('https://tproger.ru/')
        page = response.text
        soup = BeautifulSoup(page, 'html.parser')
        num_head = 0
        num_link = 0
        for head in soup.select('h2.entry-title')[num_head:3]:
            num_head += 1
            for link in soup.select('a.article-link')[num_link:num_head]:
                link = link.attrs['href']
                keyboard = types.InlineKeyboardMarkup()
                url_button = types.InlineKeyboardButton(text='Link to article', url=link)
                keyboard.add(url_button)
                bot.send_message(message.chat.id, head, reply_markup=keyboard)
                num_link += 1


@bot.message_handler(commands=['course'])
def cmd_course(message):
    if chek(message):
        usd = round(exchange_rates.rub_usd, 2)
        rub = round(exchange_rates.rub_eur, 2)
        bot.send_message(message.chat.id, 'The current rate is:\n'
                                          ' \n'
                                          f'USD:  {usd} ₽\n'
                                          f'EUR:  {rub} ₽\n', reply_markup=main_buttons)


@bot.message_handler(commands=['convertus', 'convertru', 'converteu'])
def cmd_convert(message):
    if chek(message):
        try:
            class Converter:
                def __init__(self):
                    self.user_input = int(user_input)
                    self.usd = exchange_rates.rub_usd
                    self.eur = exchange_rates.rub_eur

                def usd_in_rub(self):
                    return self.user_input * self.usd

                def eur_in_rub(self):
                    return self.user_input * self.eur

                def rub_in_usd(self):
                    return self.user_input / self.usd

                def rub_in_eur(self):
                    return self.user_input / self.eur

            sum = message.text.split()[1:]
            text = message.text.split()[:1]
            user_input = sum[0]
            command = text[0]
            converter = Converter()
            if command == '/convertru':
                sum_usd = round(converter.rub_in_usd(), 2)
                sum_eur = round(converter.rub_in_eur(), 2)
                bot.send_message(message.chat.id, f'RUB:  {user_input} ₽\n'
                                                  f'USD:  {sum_usd} $\n'
                                                  f'EUR:  {sum_eur} €')
            elif command == '/convertus':
                sum_rub = round(converter.usd_in_rub(), 2)
                bot.send_message(message.chat.id, f'USD:  {user_input} $\n'
                                                  f'RUB:  {sum_rub} ₽\n')

            elif command == '/converteu':
                sum_rub = round(converter.eur_in_rub(), 2)
                bot.send_message(message.chat.id, f'EUR:  {user_input} €\n'
                                                  f'RUB:  {sum_rub} ₽\n')

        except IndexError or ValueError:
            bot.send_message(message.chat.id, 'Enter the amount after the command')


@bot.message_handler(commands=['info'])
def cmd_info(message):
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text='VK', url="https://vk.com/id572847531")
    url_button1 = types.InlineKeyboardButton(text='Donate', url="https://vk.me/moneysend/id572847531")
    keyboard.add(url_button, url_button1)
    bot.send_message(message.chat.id, 'The bot was created on 01/23/2021.', reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'subscribe':
        cmd_subscribe(message)
    elif message.text.lower() == 'unsubscribe':
        cmd_unsubscribe(message)
    elif message.text.lower() == 'coronavirus':
        cmd_covid(message)
    elif message.text.lower() == 'new articles':
        cmd_news(message)
    elif message.text.lower() == 'Exchange Rates':
        cmd_course(message)
    elif message.text.lower() == 'info':
        cmd_info(message)
    else:
        bot.send_message(message.chat.id, 'There is no such command. More - /help')


bot.polling()
