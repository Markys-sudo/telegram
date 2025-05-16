
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()


async def greet():
    print("Some text")
    await asyncio.sleep(1)
    print("after some text")

# loop = asyncio.get_event_loop()
# loop.run_until_complete(greet())


async def say_hello(name: str) -> None:
    await asyncio.sleep(2)
    print(f"Hello, {name}!")

# loop.run_until_complete(say_hello("User1"))


async def task_():
    print("Start")
    await asyncio.sleep(10)
    print("End")

async def main():
    task = asyncio.create_task(task_())
    await asyncio.sleep(2)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("Скасовано")

# asyncio.run(main())

# name: @testAsyncioJavaR_bot
# currency_bot.py


# Task 1. Creat loop with function. Need after call function ping return text pong after 5 second

API_TOKEN = os.getenv("TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

LOG_FILE = f"log_call_{datetime.now().strftime('%Y-%m-%d')}.txt"

def get_exchange_rate(currency: str):
    try:
        res = requests.get("https://api.exchangerate-api.com/v4/latest/UAH").json()
        rate = res["rates"].get(currency.upper())
        if rate:
            return round(1 / rate, 2)
        return None
    except Exception as e:
        return None


def log_request(user_id: int, currency: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp} - User: {user_id}, Currency: {currency}\n")

def fast_callback():
    print("First priot to call")

def delayed_callback():
    print("Message from some delay")


@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    user = message.from_user
    username = user.username

    print(f"🧾 New user:")
    print(f"📛 Username: @{username if username else 'No'}")
    await message.answer("👋 Hello I'm bot. Try /ping or enter currency in test field")


@dp.message_handler(commands = 'ping')
async def ping(message: types.Message):
    print('pong function')
    await message.answer("🏓 Pong I work.")


@dp.message_handler() # commands = 'currency'
async def handle_message(message: types.Message):
    currency = message.text.strip().upper()

    loop = asyncio.get_event_loop()
    loop.call_soon(fast_callback)
    loop.call_later(5, delayed_callback)

    asyncio.create_task(async_log(message.from_user.id, currency))

    loop = asyncio.get_event_loop()
    rate = await loop.run_in_executor(None, get_exchange_rate, currency)

    if rate:
        await message.reply(f" Курс {currency} до UAH: {rate}") # добавити емодзі
    else:
        await message.reply("❌ Валюта не знайдена. Наприклад: USD, EUR")


# Task 2. Parsing(MonoAPI, PrivatAPI, API) -> async, MonoAPI(high priority)
# -> after complete 2,3 seconds run PrivatAPI/API
# * Exception and work flag -> after mono function(print('all mono done')


async def async_log(user_id, currency):
    await asyncio.sleep(0.1)
    log_request(user_id, currency)

#
if __name__ == "__main__":
    executor.start_polling(dp)
