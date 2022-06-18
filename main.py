import logging
import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from dotenv import dotenv_values
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
    cur.execute("""CREATE TABLE IF NOT EXISTS log(
       chatid BIGINT,
       message TEXT,
       	'created' DATETIME NULL DEFAULT NULL
       );
    """)
    conn.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS 'user' (
	'chatid' BIGINT NULL PRIMARY KEY,
	'username' VARCHAR(50) NULL DEFAULT NULL,
	'first_name' VARCHAR(50) NULL DEFAULT NULL,
	'last_name' VARCHAR(50) NULL DEFAULT NULL,
	'created' DATETIME NULL DEFAULT NULL,
	'upd' DATETIME NULL DEFAULT NULL
)
;
        """)
    conn.commit()


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
""")

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
    await message.answer(f'Сам {message.text}')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
