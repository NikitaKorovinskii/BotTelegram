import os
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils.graph_utils import generate_exercise_graph
from utils.export_utils import export_user_data

async def button_handler(update, context: ContextTypes.DEFAULT_TYPE):
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

async def export_handler(update, context: ContextTypes.DEFAULT_TYPE):
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
