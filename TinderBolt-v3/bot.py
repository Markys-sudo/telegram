from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from gpt import *
from util import *

from dotenv import load_dotenv
import os

load_dotenv()
TOKEN_TG = os.getenv('TOKEN_TG')
TOKEN_GPT= os.getenv('TOKEN_GPT')

async def start(update, context):
    msg = load_message('main')
    await send_photo(update, context,'main')
    await send_text(update, context, msg)
    await show_main_menu(update, context,{
        'start':'головне меню бота',
        'profile': 'генерація Tinder-профілю',
        'opener': ' повідомлення для знайомства',
        'message': 'листування від вашого імені',
        'date': 'листування із зірками',
        'gpt': 'поставити запитання чату GPT',
    })


async def gpt(update, context):
    dialog.mode ='gpt'
    await send_photo(update, context,'gpt')
    msg = load_message('gpt')
    await send_text(update, context, msg)

async def gpt_dialog(update, context):
    text = update.message.text
    promt = load_prompt('gpt')
    answer = await chatgpt.send_question(promt,text)
    await send_text(update, context, answer)

async def date(update, context):
    dialog.mode ='date'
    msg = load_message('date')
    await send_photo(update, context,'date')
    await send_text_buttons(update, context, msg, {
        'date_grande': 'Аріана Гранде',
        'date_robbie': 'Марго Роббі',
        'date_zendaya': 'Зендея',
        'date_gosling': 'Райан Гослінг',
        'date_hardy': 'Том Харді',
    })

async def date_button(update, context):
    query = update.callback_query.data
    #print(query)
    await update.callback_query.answer()
    await send_photo(update, context,query)
    await send_text(update, context, 'Гарний вибір. Ваша задача запросити дівчину/хлоця на побачення за 5 повідомлень')
    promt = load_prompt(query)
    chatgpt.set_prompt(promt)

async def date_dialog(update, context):
    text = update.message.text
    my_msg = await send_text(update, context, 'Набирає повідомлення...')
    answer = await chatgpt.add_message(text)
    await my_msg.edit_text(answer)


async def message(update, context):
    dialog.mode = 'message'
    msg = load_message('message')
    await send_photo( update, context,'message')
    await send_text_buttons(update, context, msg,{
        "message_next": 'Написати повідомлення',
        "message_date": 'Запросити на побачення'
    })
    dialog.list.clear()

async def message_dialog(update, context):
    text = update.message.text
    dialog.list.append(text)

async def message_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()

    promt = load_prompt(query)
    user_chat_history = "\n\n".join(dialog.list)

    my_message = await send_text(update, context, 'Думаю...')
    answer = await chatgpt.send_question(promt, user_chat_history)
    await my_message.edit_text(answer)
# async def button_handler(update, context):
#     query = update.callback_query
#     if query.data == 'start':
#         await send_text(update, context, 'started')
#     elif query.data == 'stop':
#         await send_text(update, context, 'stopped')

async def profile(update, context):
    dialog.mode = 'profile'
    msg = load_message('profile')
    await send_photo( update, context,'profile')
    await send_text(update, context, msg)

    dialog.user.clear()
    dialog.count = 0
    await send_text(update, context,"Скільки Вам років?")

async def profile_dialog(update, context):
    text = update.message.text
    dialog.count += 1

    if dialog.count == 1:
        dialog.user["age"] = text
        await send_text(update, context, "Ким ви працюєте?")
    elif dialog.count == 2:
        dialog.user["occupation"] = text
        await send_text(update, context, "Чи маєте хоббі?")
    elif dialog.count == 3:
        dialog.user["hobby"] = text
        await send_text(update, context, "Що вам не подобається в людях?")
    elif dialog.count == 4:
        dialog.user["annoys"] = text
        await send_text(update, context, "Мета знайомства?")
    elif dialog.count == 5:
        dialog.user["goals"] = text

    promt = load_prompt('profile')
    user_info = dialog_user_info_to_str(dialog.user)

    my_message = await send_text(update,context, "Генеруєм профіль, зачекайте!")
    answer = await chatgpt.send_question(promt, user_info)
    await my_message.edit_text(answer)

async def opener(update, context):
    dialog.mode = 'opener'
    msg = load_message('opener')
    await send_photo(update, context, 'opener')
    await send_text(update, context, msg)

    dialog.user.clear()
    dialog.count = 0
    await send_text(update, context, "ІМ'Я партнера?")


async def opener_dialog(update, context):
    text = update.message.text
    dialog.count += 1

    if dialog.count == 1:
        dialog.user["name"] = text
        await send_text(update, context, "Скільки років партнеру")
    elif dialog.count == 2:
        dialog.user["age"] = text
        await send_text(update, context, "Оцініть зовнішність 1-10 балів")
    elif dialog.count == 3:
        dialog.user["handsome"] = text
        await send_text(update, context, "Ким працює?")
    elif dialog.count == 4:
        dialog.user["occupation"] = text
        await send_text(update, context, "Мета знайомства?")
    elif dialog.count == 5:
        dialog.user["goals"] = text

    promt = load_prompt('opener')
    user_info = dialog_user_info_to_str(dialog.user)

    my_message = await send_text(update,context, "Генеруєм профіль, зачекайте!")
    answer = await chatgpt.send_question(promt, user_info)
    await my_message.edit_text(answer)

async def hello(update, context):
    if dialog.mode == 'gpt':
        await send_text(update, context, "GPT-mode " + update.message.from_user.name)
        await gpt_dialog(update, context)
    elif dialog.mode == 'date':
        await date_dialog(update, context)
    elif dialog.mode == 'message':
        await message_dialog(update, context)
    elif dialog.mode == 'profile':
        await profile_dialog(update, context)
    elif dialog.mode == 'opener':
        await opener_dialog(update, context)

dialog = Dialog()
dialog.mode = None
dialog.list = []
dialog.user = {}
dialog.count = 0


chatgpt = ChatGptService(token=TOKEN_GPT)

app = ApplicationBuilder().token(TOKEN_TG).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(CommandHandler('date', date))
app.add_handler(CommandHandler('message', message))
app.add_handler(CommandHandler('profile', profile))
app.add_handler(CommandHandler('opener', opener))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))
app.add_handler(CallbackQueryHandler(date_button, pattern="^date_.*"))
app.add_handler(CallbackQueryHandler(message_button, pattern="^message_.*"))
app.run_polling()
