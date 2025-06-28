from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, filters
)

TOKEN = "7631176083:AAGfY8H_3yOm2ei029jjyCzHF_AF7I9-mwQ"
CHANNEL_ID = 669910795
user_names = {}
ASK_NAME = 1

name_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Ввести имя", callback_data="set_name")]
])

main_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Отправить отчёт", callback_data="send_report")]
])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    user_id = update.effective_user.id
    if user_id in user_names:
        await update.message.reply_text("Ты уже ввёл имя. Можешь отправлять отчёты 👇", reply_markup=main_keyboard)
    else:
        await update.message.reply_text(
            "Привет!\n\nПеред отправкой отчётов, пожалуйста, введи своё имя:",
            reply_markup=name_keyboard
        )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "set_name":
        await query.message.reply_text("Введи своё имя:")
        return ASK_NAME

    if query.data == "send_report":
        if user_id in user_names:
            await query.message.reply_text("Отправь отчёт в виде текста, документа или фото.")
        else:
            await query.message.reply_text("Сначала введи своё имя!", reply_markup=name_keyboard)
    return ConversationHandler.END

async def save_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = update.message.text.strip()
    if not name:
        await update.message.reply_text("Имя не может быть пустым. Попробуй снова.")
        return ASK_NAME

    user_names[user_id] = name
    await update.message.reply_text(f"Спасибо, {name}! Теперь можешь отправлять отчёты 👇", reply_markup=main_keyboard)
    return ConversationHandler.END

def get_display_name(user_id):
    return user_names.get(user_id, "Неизвестный")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if update.effective_chat.type != "private" or user_id not in user_names:
        return
    text = update.message.text
    if text == "Отправить отчёт":
        return
    name = get_display_name(user_id)
    await update.message.reply_text("Текст принят и отправлен.")
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=f"Отчёт от {name}:\n\n{text}"
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if update.effective_chat.type != "private" or user_id not in user_names:
        return
    document = update.message.document
    name = get_display_name(user_id)
    await update.message.reply_text("Файл получен и отправлен.")
    await context.bot.send_document(
        chat_id=CHANNEL_ID,
        document=document.file_id,
        caption=f"Отчёт от {name}"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if update.effective_chat.type != "private" or user_id not in user_names:
        return
    photo = update.message.photo[-1]
    name = get_display_name(user_id)
    await update.message.reply_text("Фото получено и отправлено.")
    await context.bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=photo.file_id,
        caption=f"Отчёт от {name}"
    )

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    user_id = update.effective_user.id
    if user_id not in user_names:
        await update.message.reply_text("Сначала введи своё имя, чтобы начать.", reply_markup=name_keyboard)
    else:
        await update.message.reply_text("Готов принять отчёт!", reply_markup=main_keyboard)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_button)],
        states={ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_name)]},
        fallbacks=[],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.ALL, unknown))

    print("🤖 Бот запущен!")
    app.run_polling()

if __name__ == '__main__':
    main()


