from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, filters,
)
from handlers import (
    start, main_menu_handler, button_handler, export_handler,
    add_start_callback, exercise_chosen, receive_new_exercise, restart_command,
    receive_reps, receive_weight, error_handler,
    CHOOSING_EXERCISE, TYPING_NEW_EXERCISE, TYPING_REPS, TYPING_WEIGHT
)

from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_error_handler(error_handler)

    app.add_handler(CommandHandler("start", start))

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("(?i)^Добавить упражнение 🏋️‍♂️$"), add_start_callback)],
        states={
            CHOOSING_EXERCISE: [CallbackQueryHandler(exercise_chosen, pattern="^add_.*|add_new")],
            TYPING_NEW_EXERCISE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_new_exercise)],
            TYPING_REPS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_reps)],
            TYPING_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_weight)],
        },
        fallbacks=[],
        per_message=False,
    )
    app.add_handler(conv_handler)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_handler))
    app.add_handler(CommandHandler("restart", restart_command))  # 👈 регистрация команды
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^graph_"))
    app.add_handler(CallbackQueryHandler(export_handler, pattern="^export_stats$"))

    print("🚀 Бот запущен и готов к работе!")
    app.run_polling()


if __name__ == "__main__":
    main()
