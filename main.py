import sqlite3 as lite
import telebot
from config import telegram_token
from newsapi import NewsApiClient
from config import newsApi_token

newsapi = NewsApiClient(api_key=newsApi_token)

top_headlines = newsapi.get_top_headlines(q='war',
                                          category='business')


# /v2/sources
#sources = newsapi.get
print(top_headlines['articles'][0]['title'])
print(top_headlines['totalResults'])

con = lite.connect('test.db', check_same_thread=False)
cur = con.cursor()


# cur.execute("drop table if exists users;")
# cur.execute("drop table if exists categories;")
# cur.execute("drop table if exists keywords;")
cur.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY,'
            ' f_name varchar(50), l_name varchar(50));')
cur.execute('CREATE TABLE IF NOT EXISTS categories (category_id INTEGER PRIMARY KEY AUTOINCREMENT,'
            'cat_name varchar(100), user_id INTEGER)')
cur.execute('CREATE TABLE IF NOT EXISTS keywords (keyword_id integer primary key AUTOINCREMENT,'
            'word_name varchar(100), user_id INTEGER)')
data = cur.fetchone()
print(data)

# con.close() //FIXME: How correctly close current connection?

bot = telebot.TeleBot(telegram_token, parse_mode=None)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_data = cur.execute(f"SELECT * FROM users WHERE user_id = {message.from_user.id}").fetchone()
    if user_data is None:
        cur.execute(f"INSERT INTO users (user_id, f_name, l_name) VALUES "
                    f" ({message.from_user.id},"
                    f" '{message.from_user.first_name}',"
                    f" '{message.from_user.last_name}')")
        con.commit()
    bot.reply_to(message, f"Hello {message.from_user.first_name}, nice to meet you!")


@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.reply_to(message, "There is a short list of possible commands")


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, message.text)


bot.polling()
