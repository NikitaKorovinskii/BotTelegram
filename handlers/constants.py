from telegram import ReplyKeyboardMarkup

CHOOSING_EXERCISE, TYPING_NEW_EXERCISE, TYPING_REPS, TYPING_WEIGHT = range(4)

MAIN_MENU = ReplyKeyboardMarkup(
    [["Добавить упражнение 🏋️‍♂️", "Показать график 📊"]],
    resize_keyboard=True
)
