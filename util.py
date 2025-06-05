from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, BotCommand, MenuButtonCommands, BotCommandScopeChat, MenuButtonDefault
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

# надсилає в чат текстове повідомлення
async def send_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> Message:
    # Перевірка на помилковий markdown
    if text.count('_') % 2 != 0:
        warning = f"Рядок '{text}' є невалідним з погляду Markdown. Скористайтеся методом send_html()."
        print(warning)
        text = warning

    # Уникаємо проблем з юнікодом
    text = text.encode('utf16', errors='surrogatepass').decode('utf16')

    # Визначаємо об'єкт повідомлення для відповіді
    if update.message:
        return await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    elif update.callback_query and update.callback_query.message:
        return await update.callback_query.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    else:
        # На крайній випадок — надсилаємо через context.bot
        return await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.MARKDOWN)


# надсилає в чат html-повідомлення
async def send_html(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> Message:
    text = text.encode('utf16', errors='surrogatepass').decode('utf16')
    return await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.HTML)


# надсилає в чат текстове повідомлення та додає до нього кнопки
async def send_text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, buttons: dict) -> Message:
    if not isinstance(text, str):
        text = str(text)

    keyboard = [
        [InlineKeyboardButton(str(value), callback_data=str(key))]
        for key, value in buttons.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Працюємо або з update.message, або з callback_query.message
    if update.message:
        return await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    elif update.callback_query and update.callback_query.message:
        return await update.callback_query.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    else:
        raise ValueError("Немає повідомлення, куди можна відповісти.")


# надсилає в чат фото
async def send_photo(update: Update, context: ContextTypes.DEFAULT_TYPE, name: str) -> Message:
    with open('resources/images/' + name + ".jpg", 'rb') as photo:
        return await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)


# відображає команди та головне меню
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, commands: dict):
    command_list = [BotCommand(key, value) for key, value in commands.items()]
    await context.bot.set_my_commands(command_list, scope=BotCommandScopeChat(chat_id=update.effective_chat.id))
    await context.bot.set_chat_menu_button(menu_button=MenuButtonCommands(), chat_id=update.effective_chat.id)

# приховує команди та головне меню
async def hide_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=update.effective_chat.id))
    await context.bot.set_chat_menu_button(menu_button=MenuButtonDefault(), chat_id=update.effective_chat.id)


# завантажує повідомлення з папки /resources/messages/
def load_message(name):
    with open("resources/messages/" + name + ".txt", "r", encoding="utf8") as file:
        return file.read()


# завантажує промпт з папки /resources/messages/
def load_prompt(name):
    with open("resources/prompts/" + name + ".txt", "r", encoding="utf8") as file:
        return file.read()


class Dialog:
    pass
