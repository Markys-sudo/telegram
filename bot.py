from config import TOKEN_GPT, TOKEN_TG, LOG_FILE
from db import save_user, add_favorite, get_favorites
from logger import logger, gpt_logger, quiz_logger, dialog_logger
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from gpt import *
from util import *
import asyncio
import os

def log_user_action(update, text: str):
    user = update.effective_user or update.callback_query.from_user
    username = user.username or user.first_name or "Unknown"
    user_id = user.id
    dialog_logger.info(f"[{user_id}] {username}: {text}")

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
        'quiz' : 'гра "Самий розумний"',
        'photo' : 'Компьютерний зір',
        'recept': 'Кулінарний помічник',

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
    if not text:
        return  # Пропускаємо порожнє повідомлення

    gpt_logger.info(f"[{update.effective_user.id}] GPT: {text}")

    try:
        answer = await chatgpt.add_message(text)
        await send_text(update, context, answer)
    except Exception as e:
        await send_text(update, context, f"⚠️ Виникла помилка при зверненні до GPT: {e}")

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
    await send_text(update, context, 'Гарний вибір...')

    promt = load_prompt(query_data)
    chatgpt.set_prompt(promt)
    dialog.mode = 'talk'  #  відповідний режим для діалогу


async def talk_dialog(update, context):
    text = update.message.text
    if not text:
        return

    log_user_action(update, f"написав у GPT-діалозі: {text}")

    # Відправка тимчасового повідомлення
    my_msg = await send_text(update, context, '✍️ Набираємо відповідь...')

    try:
        answer = await chatgpt.add_message(text)
        # Редагування попереднього повідомлення
        await my_msg.edit_text(answer)
    except Exception as e:
        # Якщо GPT-4o впав — повідомляємо
        await my_msg.edit_text(f"⚠️ Виникла помилка при зверненні до GPT:\n{e}")

#quiz
async def quiz(update, context):
    dialog.mode = 'quiz'
    context.user_data['quiz_score'] = 0  # Скидання балів
    await send_photo(update, context, 'quiz')
    msg = load_message('quiz')
    await send_text_buttons(update, context, msg, {
        'quiz_science': 'Наука і технології',
        'quiz_world': 'Світ навколо нас',
        'quiz_culture': 'Культура та мистецтво',
        'quiz_history': 'Історія та сучасність',
    })

async def quiz_button(update, context):
    callback = update.callback_query
    query_data = callback.data
    dialog.mode = 'quiz'

    await callback.answer()
    log_user_action(update, f"натиснув кнопку: {query_data}")

    # Якщо користувач натиснув "Завершити"
    if query_data == 'quiz_end':
        score = context.user_data.get('quiz_score', 0)
        await send_text(update, context, f"🏁 Вікторину завершено. Ваш результат: {score} правильних відповідей.")
        return

    # Надсилання фото
    try:
        await send_photo(update, context, query_data)
    except FileNotFoundError:
        await send_text(update, context, "⚠️ Зображення не знайдено.")

    await send_text(update, context, '🎯 Ви обрали категорію. Переходимо до запитань!')

    prompt = load_prompt(query_data)
    context.user_data['quiz_prompt'] = prompt
    context.user_data['quiz_score'] = 0

    await ask_new_question(update, context, prompt)

async def ask_new_question(update, context, prompt):
    await send_text(update, context, "❓ Питання готується...")

    raw_question = await chatgpt.send_question(prompt, "Згенеруй одне коротке питання українською мовою з 4 варіантами відповіді та чітко зазнач правильно відповідь. Формат обов’язковий:\n"
"Питання: ...\nА) ...\nБ) ...\nВ) ...\nГ) ...\nПравильна відповідь: <лише одна літера А/Б/В/Г>"
)

    parsed = parse_quiz_question(raw_question)

    if not parsed['question'] or len(parsed['options']) != 4 or not parsed['correct']:
        await send_text(update, context, "⚠️ Сталася помилка при генерації питання. Спробуйте ще раз.")
        return

    context.user_data['quiz_correct'] = parsed['correct']
    await send_text_buttons(update, context, parsed['question'], {
        **parsed['options'],
        'quiz_end': '🏁 Завершити'
    })
    #await send_text(update, context, f"🧪 Тестовий вивід GPT:\n\n{raw_question}")

def parse_quiz_question(text: str) -> dict:
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    result = {
        'question': '',
        'options': {},
        'correct': ''
    }

    option_map = {'А': 'quiz_A', 'Б': 'quiz_B', 'В': 'quiz_C', 'Г': 'quiz_D'}

    for line in lines:
        if line.lower().startswith("питання:"):
            result['question'] = line.partition(':')[2].strip()
        elif any(line.startswith(f"{k})") for k in option_map):
            prefix = line[0]
            key = option_map.get(prefix)
            result['options'][key] = line[2:].strip()
        elif "правильна відповідь" in line.lower():
            letter = line.strip()[-1].upper()
            result['correct'] = option_map.get(letter, '')

    # Валідація
    if not result['question'] or len(result['options']) != 4 or not result['correct']:
        return {'question': '', 'options': {}, 'correct': ''}

    return result

async def quiz_answer(update, context):
    callback = update.callback_query
    answer = callback.data
    correct = context.user_data.get('quiz_correct')
    user_id = callback.from_user.id

    await callback.answer()

    if answer == 'quiz_end':
        score = context.user_data.get('quiz_score', 0)
        quiz_logger.info(f"[{user_id}] Завершив вікторину. Результат: {score}")
        await send_text(update, context, f"🏁 Вікторину завершено. Ваш результат: {score} правильних відповідей.")
        return

    if not correct:
        quiz_logger.warning(f"[{user_id}] Не вдалося перевірити відповідь.")
        await send_text(update, context, "⚠️ Не вдалося перевірити відповідь. Спробуйте ще раз.")
        return

    if answer == correct:
        context.user_data['quiz_score'] += 1
        quiz_logger.info(f"[{user_id}] ✅ Правильно обрав: {answer}")
        await send_text(update, context, "✅ Вірно!")
    else:
        correct_letter = correct[-1]
        quiz_logger.info(f"[{user_id}] ❌ Неправильно. Обрав: {answer}, правильно: {correct}")
        await send_text(update, context, f"❌ Невірно. Правильна відповідь: {correct_letter}")

    await asyncio.sleep(1)
    await send_text(update, context, "📚 Наступне питання готується...")

    prompt = context.user_data.get('quiz_prompt')
    if not prompt:
        await send_text(update, context, "⚠️ Не обрано категорію вікторини. Натисніть /quiz для початку.")
        return

    await ask_new_question(update, context, prompt)

#photo
async def photo_mode_start(update, context):
    dialog.mode = 'photo'
    await send_text(update, context, "📸 Надішліть мені зображення для обробки.")

async def photo_handler(update, context):
    if dialog.mode != 'photo':
        await send_text(update, context, "📷 Зображення можна надсилати лише в режимі /photo.")
        return

    user = update.effective_user
    photo = update.message.photo[-1]

    file = await context.bot.get_file(photo.file_id)
    os.makedirs("user_photos", exist_ok=True)
    file_path = f"user_photos/{user.id}_{photo.file_id}.jpg"
    await file.download_to_drive(file_path)

    await send_text(update, context, "🧠 Аналізуємо зображення...")

    try:
        result = await chatgpt.describe_image(file_path)
        await send_text(update, context, f"📷 GPT-4o каже: {result}")
    except Exception as e:
        await send_text(update, context, f"⚠️ Помилка аналізу GPT-4o: {e}")
    dialog.mode = 'main'

    await asyncio.sleep(2)
    await send_text(update, context, "🏠 Повертаємось до головного меню.")
    await start(update, context)

#recept
async def recept(update, context):

    user = update.effective_user
    save_user(user)  # Зберегти користувача

    dialog.mode ='recept'

    await send_photo(update, context,'recept')

    msg = load_message('recept')
    await send_text(update, context, msg)

async def recept_button(update, context):
    query = update.callback_query
    await query.answer()

    log_user_action(update, f"натиснув: {query}")

    if query.data == 'recept_next':
        ingredients = context.user_data.get('ingredients', '')
        promt = load_prompt('recept')
        promt_filled = promt.format(ingredients=ingredients)
        chatgpt.set_prompt(promt_filled)
        answer = await chatgpt.send_message_list()

        await send_text_buttons(update, context, answer, {
            "recept_next": 'Ще рецепти',
            "recept_save": '📌 Додати в обране',
            "recept_favorites": '🍴 Мої обрані рецепти',
            "recept_end": 'Закінчити'
        })
    elif query.data == 'recept_save':
        user_id = query.from_user.id
        recipe_text = query.message.text
        add_favorite(user_id, recipe_text)
        await send_text(update, context, "✅ Рецепт додано до обраного!")

    elif query.data == 'recept_favorites':
        await favorites(update, context)  # той самий хендлер, що і для /favorites

    elif query.data == 'recept_end':
        await start(update, context)  # той самий хендлер, що і для /start


async def recept_dialog(update, context):
    if dialog.mode != 'recept':
        return
    text = update.message.text if update.message and update.message.text else ''
    if not text:
        return  # Пропускаємо порожнє повідомлення

    context.user_data['ingredients'] = text
    chatgpt.message_list.clear()

    gpt_logger.info(f"[{update.effective_user.id}] GPT: {text}")

    try:
        promt_template = load_prompt('recept')
        promt = promt_template.format(ingredients=text)
        chatgpt.set_prompt(promt)  # просто встановлюємо prompt
        answer = await chatgpt.send_message_list()  # отримуємо відповідь GPT
        await send_text_buttons(update, context, answer, {
            "recept_next": 'Ще рецепти',
            "recept_save": '📌 Додати в обране',
            "recept_favorites": '🍴 Мої обрані рецепти',
            "recept_end": 'Закінчити'
        })

    except Exception as e:
        await send_text(update, context, f"⚠️ Виникла помилка при зверненні до GPT: {e}")

async def favorites(update, context):
    user_id = update.effective_user.id
    favs = get_favorites(user_id)
    if not favs:
        await send_text(update, context, "📭 У вас ще немає збережених рецептів.")
    else:
        await send_text(update, context, "📚 Ваші улюблені рецепти:")
        for recipe in favs:
            await send_text(update, context, recipe)


async def dialog_mode(update, context):
    if dialog.mode == 'gpt':
        await send_text(update, context, "GPT-mode " + update.message.from_user.name)
        await gpt_dialog(update, context)
    elif dialog.mode == 'random_fact':
        await random_fact(update, context)
    elif dialog.mode == 'talk':
        await talk_dialog(update, context)
    elif dialog.mode == 'quiz':
        await send_text(update, context, "✋ Надішліть відповідь, натиснувши одну з кнопок.")

    elif dialog.mode == 'photo':
        await photo_handler(update, context)
    elif dialog.mode == 'recept':
        await recept_dialog(update, context)

dialog = Dialog()
dialog.mode = 'main'

chatgpt = ChatGptService(token=TOKEN_GPT)
app = ApplicationBuilder().token(TOKEN_TG).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random_fact))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(CommandHandler('talk', talk))
app.add_handler(CommandHandler('quiz', quiz))
app.add_handler(CommandHandler('photo', photo_mode_start))
app.add_handler(CommandHandler('recept', recept))
app.add_handler(CommandHandler('favorites', favorites))


app.add_handler(CallbackQueryHandler(quiz_answer, pattern="^quiz_[A-D]$"))
app.add_handler(CallbackQueryHandler(button_fact, pattern="^fact_.*"))
app.add_handler(CallbackQueryHandler(talk_button, pattern="^talk_.*"))
app.add_handler(CallbackQueryHandler(quiz_button, pattern="^quiz_.*"))
app.add_handler(CallbackQueryHandler(recept_button, pattern="^recept_.*"))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), dialog_mode))
app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

if __name__ == '__main__':
    app.run_polling()
