from config import TOKEN_GPT, TOKEN_TG, LOG_FILE
import logging
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from gpt import *
from util import *

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_user_action(update, text: str):
    user = update.effective_user or update.callback_query.from_user
    username = user.username or user.first_name or "Unknown"
    user_id = user.id
    logger.info(f"[{user_id}] {username}: {text}")


async def start(update, context):
    dialog.mode = 'main'
    msg = load_message('main')
    await send_photo(update, context,'avatar_main')
    await send_text(update, context, msg)
    await show_main_menu(update, context,{
        'start':'головне меню бота',
        'random': 'цікавий факт',
        'gpt' : 'розмова зі ШІ',
        'talk' : 'Діалог з відомою особистістю',
    })
    chatgpt.message_list.clear()

async def random_fact(update, context):
    text = update.message.text if update.message and update.message.text else ''

    log_user_action(update, f"написав: {text}")
    dialog.mode = 'random_fact'

    await send_photo(update, context, 'fact')
    promt = load_prompt('random_fact')

    try:
        answer = await chatgpt.send_question(promt, text)
        await send_text_buttons(update, context, answer, {
            "fact_random": 'Ще цікавий факт',
            "fact_start": 'Закінчити'
        })
    except Exception as e:
        error_text = f"⚠️ Виникла помилка при генерації факту: {e}"
        await send_text(update, context, error_text)
        log_user_action(update, f" — {error_text}")



async def button_fact(update, context):
    query = update.callback_query
    await query.answer()

    log_user_action(update, f"натиснув: {query}")

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

    log_user_action(update, f"написав: {text}")

    # promt = load_prompt('gpt')
    answer = await chatgpt.add_message(text)
    await send_text(update, context, answer)


async def talk(update, context):
    dialog.mode ='talk'
    msg = load_message('talk')
    await send_photo(update, context,'talk')
    await send_text_buttons(update, context, msg, {
        'talk_mask': 'Ілон Маск',
        'talk_jobs': 'Стів Джобс',
        'talk_geyts': 'Біл Гейтс',

    })


async def talk_button(update, context):
    callback = update.callback_query
    query_data = callback.data

    await callback.answer()
    log_user_action(update, f"натиснув кнопку: {query_data}")

    await send_photo(update, context, query_data)
    await send_text(update, context, 'Гарний вибір.')

    promt = load_prompt(query_data)
    chatgpt.set_prompt(promt)
    dialog.mode = 'talk'  #  відповідний режим для діалогу


async def talk_dialog(update, context):
    text = update.message.text
    if not text:
        return

    log_user_action(update, f"написав у GPT-діалозі: {text}")

    my_msg = await send_text(update, context, 'Набирає повідомлення...')
    answer = await chatgpt.add_message(text)
    await my_msg.edit_text(answer)



async def dialog_mode(update, context):
    if dialog.mode == 'gpt':
        await send_text(update, context, "GPT-mode " + update.message.from_user.name)
        await gpt_dialog(update, context)
    elif dialog.mode == 'random_fact':
        await random_fact(update, context)
    elif dialog.mode == 'talk':
        await talk_dialog(update, context)

dialog = Dialog()
dialog.mode = 'main'

chatgpt = ChatGptService(token=TOKEN_GPT)
app = ApplicationBuilder().token(TOKEN_TG).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random_fact))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(CommandHandler('talk', talk))

app.add_handler(CallbackQueryHandler(button_fact, pattern="^fact_.*"))
app.add_handler(CallbackQueryHandler(talk_button, pattern="^talk_.*"))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), dialog_mode))

if __name__ == '__main__':
    app.run_polling()
