from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils.excel_utils import get_user_exercises
from handlers.constants import MAIN_MENU
from handlers import error_handler

def get_name(update):
    user = update.effective_user
    return user.first_name or user.username or "друг"

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    name = get_name(update)
    text = (
        f"👋 Привет, {name}! Добро пожаловать в WorkOut бот! 🏋️‍♂️\n"
        "Выбери, что хочешь сделать сегодня:"
    )
    await update.message.reply_text(text, reply_markup=MAIN_MENU)

async def main_menu_handler(update, context: ContextTypes.DEFAULT_TYPE):
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
