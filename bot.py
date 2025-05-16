from dotenv import load_dotenv
import os
import logging
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from gpt import *
from util import *

load_dotenv()
TOKEN_TG = os.getenv('TOKEN_TG')
TOKEN_GPT= os.getenv('TOKEN_GPT')

logging.basicConfig(filename='bot.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def start(update, context):
    user = update.effective_user
    username = user.username or user.first_name or "Unknown"
    user_id = user.id
    text = update.message.text if update.message and update.message.text else ''

    logger.info(f"[{user_id}] {username} написав: {text}")

    dialog.mode = 'main'
    msg = load_message('main')
    await send_photo(update, context,'main')
    await send_text(update, context, msg)
    await show_main_menu(update, context,{
        'start':'головне меню бота',
        'random': 'цікавий факт',
    })


async def random_fact(update, context):
    user = update.effective_user
    username = user.username or user.first_name or "Unknown"
    user_id = user.id
    text = update.message.text if update.message and update.message.text else ''

    logger.info(f"[{user_id}] {username} написав: {text}")

    dialog.mode = 'random_fact'
    await send_photo(update, context, 'fact')

    text = update.message.text if update.message and update.message.text else ''
    promt = load_prompt('random_fact')

    try:
        answer = await chatgpt.send_question(promt, text)
        # msg = await send_text(update, context, answer)
        await send_text_buttons(update, context, answer, {
            "fact_random": 'Ще цікавий факт',
            "fact_start": 'Закінчити'
        })
    except Exception as e:
        # Наприклад, логування або відправка повідомлення про помилку
        await send_text(update, context, f"⚠️ Виникла помилка: {e}")

    # dialog.list.clear()

async def button_fact(update, context):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    username = user.username or user.first_name or "Unknown"
    user_id = user.id
    logger.info(f"[{user_id}] {username} натиснув кнопку: {query.data}")

    if query.data == 'fact_random':
        text = query.message.text if query.message and query.message.text else ''
        promt = load_prompt('random_fact')
        answer = await chatgpt.send_question(promt, text)

        # Тепер надсилаємо одне повідомлення з текстом і кнопками
        await send_text_buttons(update, context, answer, {
            "fact_random": 'Ще цікавий факт',
            "fact_start": 'Закінчити'
        })

    elif query.data == 'fact_start':
        dialog.mode = 'main'
        await start(update, context)  # той самий хендлер, що і для /start


# async def button_fact(update, context):
#     query = update.callback_query.data
#     if query == 'fact_random':
#         text = update.message.text if update.message and update.message.text else ''
#         promt = load_prompt('random_fact')
#         await chatgpt.send_question(promt, text)
#     if query == 'fact_start':
#         dialog.mode = 'main'

async def hello(update, context):
    if dialog.mode == 'start':
        await start(update, context)
    elif dialog.mode == 'random':
        await random_fact(update, context)

dialog = Dialog()
dialog.mode = 'main'

chatgpt = ChatGptService(token=TOKEN_GPT)
app = ApplicationBuilder().token(TOKEN_TG).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random_fact))

app.add_handler(CallbackQueryHandler(button_fact, pattern="^fact_.*"))
app.run_polling()