from config import TOKEN_GPT, TOKEN_TG
import logging
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from gpt import *
from util import *

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
    await send_photo(update, context,'avatar_main')
    await send_text(update, context, msg)
    await show_main_menu(update, context,{
        'start':'головне меню бота',
        'random': 'цікавий факт',
        'gpt' : 'розмова зі ШІ'
    })
    chatgpt.message_list.clear()

async def random_fact(update, context):
    user = update.effective_user
    username = user.username or user.first_name or "Unknown"
    user_id = user.id
    text = update.message.text if update.message and update.message.text else ''

    logger.info(f"[{user_id}] {username} написав: {text}")
    await send_photo(update, context, 'fact')
    promt = load_prompt('random_fact')

    try:
        answer = await chatgpt.send_question(promt, text)
        await send_text_buttons(update, context, answer, {
            "fact_random": 'Ще цікавий факт',
            "fact_start": 'Закінчити'
        })
    except Exception as e:
        # Наприклад, логування або відправлення повідомлення про помилку
        await send_text(update, context, f"⚠️ Виникла помилка: {e}")
        logger.error(f"Помилка при генерації факту: {e}")
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
        await start(update, context)  # той самий хендлер, що і для /start


async def gpt(update, context):
    dialog.mode ='gpt'
    await send_photo(update, context,'gpt')
    msg = load_message('gpt')
    await send_text(update, context, msg)

async def gpt_dialog(update, context):
    text = update.message.text if update.message and update.message.text else ''
    # promt = load_prompt('gpt')
    answer = await chatgpt.add_message(text)
    await send_text(update, context, answer)


async def dialog_mode(update, context):
    if dialog.mode == 'gpt':
        await send_text(update, context, "GPT-mode " + update.message.from_user.name)
        await gpt_dialog(update, context)

dialog = Dialog()
dialog.mode = 'main'

chatgpt = ChatGptService(token=TOKEN_GPT)
app = ApplicationBuilder().token(TOKEN_TG).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random_fact))
app.add_handler(CommandHandler('gpt', gpt))

app.add_handler(CallbackQueryHandler(button_fact, pattern="^fact_.*"))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), dialog_mode))

if __name__ == '__main__':
    app.run_polling()
