from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
import logging
from utils.excel_utils import save_to_excel, get_user_exercises
from handlers.constants import (
    CHOOSING_EXERCISE, TYPING_NEW_EXERCISE, TYPING_REPS, TYPING_WEIGHT, MAIN_MENU
)

def get_name(update):
    user = update.effective_user
    return user.first_name or user.username or "друг"

async def add_start_callback(update, context: ContextTypes.DEFAULT_TYPE):
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

async def exercise_chosen(update, context: ContextTypes.DEFAULT_TYPE):
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

async def receive_new_exercise(update, context: ContextTypes.DEFAULT_TYPE):
    name = get_name(update)
    context.user_data["exercise"] = update.message.text.strip()
    await update.message.reply_text(f"🔥 {name}, сколько раз ты повторил это упражнение?")
    return TYPING_REPS

async def receive_reps(update, context: ContextTypes.DEFAULT_TYPE):
    name = get_name(update)
    reps_text = update.message.text.strip()
    if not reps_text.isdigit():
        await update.message.reply_text("❌ Пожалуйста, введи корректное число повторений без букв и символов! Попробуй ещё раз:")
        return TYPING_REPS
    context.user_data["reps"] = reps_text
    await update.message.reply_text(f"⚖️ {name}, какой вес ты использовал?")
    return TYPING_WEIGHT

async def receive_weight(update, context: ContextTypes.DEFAULT_TYPE):
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
    return -1  # ConversationHandler.END
