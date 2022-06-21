import logging
import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from dotenv import dotenv_values
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo
import os

config = dotenv_values("config.env")

API_TOKEN = config['TELEGRAM_BOT_API_KEY']

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

sql_init = False

if not os.path.exists('mycash.db'):
    sql_init = True
conn = sqlite3.connect('mycash.db')
cur = conn.cursor()

if sql_init:
    with open("migrations/2022_06_18_db_init.sql", "r") as file:
        mass = file.read()
        for sql_item in mass.split(';'):
            if len(sql_item) > 5:
                cur.execute(sql_item)
                conn.commit()


def get_keyboard():
    webAppTest = types.WebAppInfo("https://telegram.mihailgok.ru")  # создаем webappinfo - формат хранения url
    return types.InlineKeyboardMarkup().row(
        types.InlineKeyboardButton(text="Тестовая страница", web_app=webAppTest, url="https://telegram.mihailgok.ru")
    )


def webAppKeyboard():  # создание клавиатуры с webapp кнопкой
    keyboard = types.ReplyKeyboardMarkup(row_width=1)  # создаем клавиатуру
    webAppTest = types.WebAppInfo("https://telegram.mihailgok.ru")  # создаем webappinfo - формат хранения url
    one_butt = types.KeyboardButton(text="Тестовая страница", web_app=webAppTest)  # создаем кнопку типа webapp
    keyboard.add(one_butt)  # добавляем кнопки в клавиатуру

    return keyboard  # возвращаем клавиатуру


async def send_to_db(sql):
    cur.execute(sql)
    conn.commit()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start`
    """
    await send_to_db(f"""INSERT INTO log (`chatid`, `message`,`created`) 
           VALUES('{message.from_user.id}', '{message.text}',datetime('now'));""")
    await send_to_db(f"""INSERT OR IGNORE INTO USER (`chatid`,`username`,`first_name`,`last_name`,`created`,`upd`) 
    VALUES ('{message.from_user.id}',
    '{message.from_user.username}',
    '{message.from_user.first_name}',
    '{message.from_user.last_name}',
    datetime('now'),datetime('now'));""")

    # upd user info
    await send_to_db(f"""UPDATE USER SET 
    `username` = '{message.from_user.username}',
    `first_name` = '{message.from_user.first_name}',
    `last_name` = '{message.from_user.last_name}',
    `upd` = datetime('now') 
    where `chatid`={message.from_user.id}
""")
    await message.answer(f"""Привет уважаемый {message.from_user.first_name}! 
Я помогу учесть Ваши доходы и расходы. 
    
Помощь по команде /help
""", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="test",
web_app=WebAppInfo(url="https://script.google.com/macros/s/AKfycby3lyo0yU4z2wPI6li2JK1N2w4J9UT52xQ3HwZcL9j_DdzlAx0/exec")))
                         )


@dp.message_handler(commands=['help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/help`
    """
    await message.answer("""Здесь будет справочная инофрмация, 
    
жми 👉 /start""")


@dp.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)
    # cur.execute("ВАШ-SQL-ЗАПРОС-ЗДЕСЬ;")
    chatid = message.from_user.id
    await send_to_db(f"""INSERT INTO log (`chatid`, `message`,`created`) 
               VALUES('{message.from_user.id}', '{message.text}',datetime('now'));""")
    await message.answer(f'Сам {message.text}',reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text=f"Сайт {message.text}",
web_app=WebAppInfo(url=f"https://{message.text}"))))


@dp.message_handler(content_types="answerWebAppQuery") #получаем отправленные данные
def answer(WebAppInfo):
   print(WebAppInfo) #вся информация о сообщении
   print(WebAppInfo.web_app_data.data) #конкретно то что мы передали в бота
   bot.send_message(WebAppInfo.chat.id, f"получили инофрмацию из веб-приложения: {WebAppInfo.web_app_data.data}")
   #отправляем сообщение в ответ на отправку данных из веб-приложения

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
