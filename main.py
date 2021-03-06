import sqlite3 as lite
from typing import List, Any
import telebot
from config import telegram_token
from newsapi import NewsApiClient
from config import newsApi_token

state = 0

con = lite.connect('test.db', check_same_thread=False)
cur = con.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY,'
            ' f_name varchar(50), l_name varchar(50));')
cur.execute('CREATE TABLE IF NOT EXISTS categories (category_id INTEGER PRIMARY KEY AUTOINCREMENT,'
            'cat_name varchar(100), user_id INTEGER)')
cur.execute('CREATE TABLE IF NOT EXISTS keywords (keyword_id integer primary key AUTOINCREMENT,'
            'word_name varchar(100), user_id INTEGER)')
data = cur.fetchone()

bot = telebot.TeleBot(telegram_token, parse_mode=None)
keyboard = telebot.types.ReplyKeyboardMarkup(True)
keyboard.row('Add news category', 'Add news keyword')
keyboard.row('Show my categories', 'Show my keywords')
keyboard.row('Remove category', 'Remove keyword')


def add_category(message):
    cat_data = cur.execute(f"SELECT * FROM categories WHERE cat_name = '{message.text}' "
                           f"AND user_id = {message.from_user.id}").fetchone()
    print(cat_data)
    if cat_data is None:
        cur.execute(f"INSERT INTO categories (cat_name, user_id) VALUES "
                    f" ('{message.text}',"
                    f" {message.from_user.id})")
        con.commit()
    else:
        bot.reply_to(message, "This category is already exists")


def add_keyword(message):
    key_data = cur.execute(f"SELECT * FROM keywords WHERE word_name = '{message.text}' "
                           f"AND user_id = {message.from_user.id}").fetchone()
    if key_data is None:
        cur.execute(f"INSERT INTO keywords (word_name, user_id) VALUES "
                    f" ('{message.text}',"
                    f" {message.from_user.id})")
        con.commit()
    else:
        bot.reply_to(message, "This keyword is already exists")


def show_categories(message):
    user_cats = cur.execute(f"SELECT cat_name FROM categories WHERE user_id = {message.from_user.id}").fetchall()
    if user_cats is None:
        bot.reply_to(message, "You haven't any categories")
    else:
        bot.reply_to(message, f"List of your chosen categories {user_cats}")


def show_keywords(message):
    user_keyw = cur.execute(f"SELECT word_name FROM keywords WHERE user_id = {message.from_user.id}").fetchall()
    if user_keyw is None:
        bot.reply_to(message, "You haven't any keywords")
    else:
        bot.reply_to(message, f"List of your chosen categories : {user_keyw}")


def remove_category(message):
    cur.execute(f"DELETE FROM categories WHERE cat_name = '{message.text}'")
    con.commit()


def remove_keyword(message):
    cur.execute(f"DELETE FROM keywords WHERE word_name = '{message.text}'")
    con.commit()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_data = cur.execute(f"SELECT * FROM users WHERE user_id = {message.from_user.id}").fetchone()
    if user_data is None:
        cur.execute(f"INSERT INTO users (user_id, f_name, l_name) VALUES "
                    f" ({message.from_user.id},"
                    f" '{message.from_user.first_name}',"
                    f" '{message.from_user.last_name}')")
        con.commit()
    bot.reply_to(message, f"Hello {message.from_user.first_name}, nice to meet you!\n Choose what you want!",
                 reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.reply_to(message, f"msg = {message.text} There is a short list of possible commands\n"
                          f"/start - this command registry user (if he isn't registry) and opens main menu\n"
                          f"/show_news - this command show news based on chosen categories and keywords\n")


@bot.message_handler(commands=['show_news'])
def get_news(message):
    bot.reply_to(message, "News list : \n")
    newsapi = NewsApiClient(api_key=newsApi_token)
    user_cats: List[Any] = cur.execute(
        f"SELECT cat_name FROM categories WHERE user_id = {message.from_user.id}").fetchall()
    user_keyw: List[Any] = cur.execute(
        f"SELECT word_name FROM keywords WHERE user_id = {message.from_user.id}").fetchall()

    category_list = [item for t in user_cats for item in t]
    keyword_list = [item for t in user_keyw for item in t]

    for cat in category_list:
        for keyword in keyword_list:
            top_headlines = newsapi.get_top_headlines(q=keyword,
                                                      category=cat,
                                                      page_size=10,
                                                      page=1)
            bot.reply_to(message, f"News category is \"{cat}\"\n News keyword is \"{keyword}\"\n")

            if top_headlines['totalResults']:
                if top_headlines['totalResults'] > 10:
                    cnt = 10
                else:
                    cnt = top_headlines['totalResults']
                for i in range(cnt):

                    bot.reply_to(message, f"====== {i+1} Article =========\n")
                    bot.reply_to(message, f" Title \n {top_headlines['articles'][i]['title']}\n"
                                          f" Link {top_headlines['articles'][i]['url']}\n")
            else:
                bot.reply_to(message, "Can't found any news!\n")


@bot.message_handler(content_types=["text"])
def main(message):
    global state

    if state == 1:
        print(message.text)
        add_category(message)
        state = 0
    elif state == 2:
        add_keyword(message)
        state = 0
    elif state == 5:
        remove_category(message)
        state = 0
    elif state == 6:
        remove_keyword(message)
        state = 0

    bot.send_message(message.chat.id, 'done', reply_markup=telebot.types.ReplyKeyboardRemove())
    if message.text == "Add news category":
        state = 1
        keyboard1 = telebot.types.ReplyKeyboardMarkup(True)
        keyboard1.row('sports', 'business')
        keyboard1.row('entertainment', 'general')
        keyboard1.row('health', 'science')
        keyboard1.row('technology')
        bot.send_message(message.chat.id, "Choose the possible categories", reply_markup=keyboard1)
    elif message.text == 'Add news keyword':
        state = 2
        bot.send_message(message.chat.id, "Enter new keyword")
    elif message.text == 'Show my categories':
        show_categories(message)
    elif message.text == 'Show my keywords':
        show_keywords(message)
    elif message.text == 'Remove category':
        state = 5
        bot.send_message(message.chat.id, "Enter name of category what you want to delete")
    elif message.text == 'Remove keyword':
        state = 6
        bot.send_message(message.chat.id, "Enter name of keyword what you want to delete")


bot.polling()
