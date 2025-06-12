async def error_handler(update: object, context):
    print(f"⚠️ Произошла ошибка: {context.error}")

    if update is not None:
        try:
            chat_id = None
            if hasattr(update, "effective_chat") and update.effective_chat:
                chat_id = update.effective_chat.id
            elif hasattr(update, "message") and update.message:
                chat_id = update.message.chat.id
            elif hasattr(update, "callback_query") and update.callback_query:
                chat_id = update.callback_query.message.chat.id

            if chat_id:
                await context.bot.send_message(chat_id=chat_id, text=f"❗️ Произошла ошибка:\n{context.error}")
        except Exception as e:
            print(f"Не удалось отправить сообщение об ошибке: {e}")
