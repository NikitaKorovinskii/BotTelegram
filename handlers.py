from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
)
from telegram.ext import ContextTypes, ConversationHandler
import os
import logging
from excel_utils import save_to_excel, get_user_exercises
from graph_utils import generate_exercise_graph
from export_utils import export_user_data

logging.basicConfig(level=logging.INFO)

CHOOSING_EXERCISE, TYPING_NEW_EXERCISE, TYPING_REPS, TYPING_WEIGHT = range(4)

MAIN_MENU = ReplyKeyboardMarkup(
    [["Добавить упражнение 🏋️‍♂️", "Показать график 📊"]],
    resize_keyboard=True
)

def get_name(update: Update):
    user = update.effective_user
    return user.first_name or user.username or "друг"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = get_name(update)
    text = (
        f"👋 Привет, {name}! Добро пожаловать в WorkOut бот! 🏋️‍♂️\n"
        "Выбери, что хочешь сделать сегодня:"
    )
    await update.message.reply_text(text, reply_markup=MAIN_MENU)

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    name = get_name(update)
    user = update.effective_user
    username = user.username or str(user.id)

    if text == "Показать график 📊":
        exercises = get_user_exercises(username)
        if not exercises:
            await update.message.reply_text(
                f"📉 Ой, {name}, у тебя пока нет данных для графиков. "
                "Добавь хотя бы одно упражнение, и мы увидим твой прогресс! 🚀"
            )
            return
        buttons = [[InlineKeyboardButton(ex, callback_data=f"graph_{ex}")] for ex in exercises]
        buttons.append([InlineKeyboardButton("📤 Выгрузить статистику", callback_data="export_stats")])
        await update.message.reply_text(
            f"💪 Отлично, {name}! Выбери упражнение, чтобы посмотреть график:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await update.message.reply_text(
            f"😅 Хм, {name}, я не понял эту команду. "
            "Пожалуйста, выбирай действие через кнопки ниже 👇"
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    username = user.username or str(user.id)
    data = query.data

    if data.startswith("graph_"):
        exercise = data.replace("graph_", "")
        success = generate_exercise_graph(exercise, username)
        if success:
            with open("graph.png", "rb") as photo:
                await query.message.reply_photo(photo)
            os.remove("graph.png")
        else:
            await query.message.reply_text("⚠️ Не удалось построить график по этому упражнению. Попробуй другое 😉")

async def export_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    username = user.username or str(user.id)

    filepath = export_user_data(username)
    if filepath:
        with open(filepath, "rb") as file:
            await query.message.reply_document(file, filename=os.path.basename(filepath))
        os.remove(filepath)
    else:
        await query.message.reply_text("⚠️ У тебя нет данных для выгрузки. Добавь упражнения, чтобы сохранить статистику!")

async def add_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = get_name(update)
    user = update.effective_user
    username = user.username or str(user.id)

    exercises = get_user_exercises(username)
    buttons = [[InlineKeyboardButton(ex, callback_data=f"add_{ex}")] for ex in exercises]
    buttons.append([InlineKeyboardButton("➕ Добавить новое упражнение", callback_data="add_new")])

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            f"💡 {name}, выбери упражнение или добавь новое:", reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await update.message.reply_text(
            f"💡 {name}, выбери упражнение или добавь новое:", reply_markup=InlineKeyboardMarkup(buttons)
        )
    return CHOOSING_EXERCISE

async def exercise_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    logging.info(f"Callback data received: {query.data}")
    await query.answer()
    data = query.data
    name = get_name(update)

    if data == "add_new":
        await query.edit_message_text(f"📝 {name}, введи название нового упражнения:")
        return TYPING_NEW_EXERCISE
    else:
        exercise = data.replace("add_", "")
        context.user_data["exercise"] = exercise
        await query.edit_message_text(f"✅ Отлично, {name}! Ты выбрал: {exercise}.\nСколько повторений сделал? 🔥")
        return TYPING_REPS

async def receive_new_exercise(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = get_name(update)
    context.user_data["exercise"] = update.message.text.strip()
    await update.message.reply_text(f"🔥 {name}, сколько раз ты повторил это упражнение?")
    return TYPING_REPS

async def receive_reps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = get_name(update)
    reps_text = update.message.text.strip()
    if not reps_text.isdigit():
        await update.message.reply_text("❌ Пожалуйста, введи корректное число повторений без букв и символов! Попробуй ещё раз:")
        return TYPING_REPS
    context.user_data["reps"] = reps_text
    await update.message.reply_text(f"⚖️ {name}, какой вес ты использовал?")
    return TYPING_WEIGHT

async def receive_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = get_name(update)
    weight_text = update.message.text.replace(',', '.').strip()
    try:
        weight_val = float(weight_text)
        if weight_val < 0:
            raise ValueError()
    except ValueError:
        await update.message.reply_text("❌ Введи, пожалуйста, корректное положительное число веса, например: 15.5")
        return TYPING_WEIGHT

    context.user_data["weight"] = weight_text

    user = update.effective_user
    username = user.username or str(user.id)
    save_to_excel(username, context.user_data)

    await update.message.reply_text(f"🎉 Отлично, {name}! Я записал твой результат. Возвращаемся в главное меню 🏠", reply_markup=MAIN_MENU)
    return ConversationHandler.END

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error(msg="Exception while handling an update:", exc_info=context.error)
    if update and hasattr(update, "message") and update.message:
        await update.message.reply_text("⚠️ Произошла ошибка, попробуйте ещё раз позже.")
