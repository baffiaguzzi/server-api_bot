from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not chat:
        return

    text = "Hey! 👋\nChoose what you want to do:"

    keyboard = [
        [InlineKeyboardButton("🌐 Check SERVER", callback_data="main:server")],
        [InlineKeyboardButton("📡 Check ENDPOINTS", callback_data="main:endpoints")],
        [InlineKeyboardButton("📊 Stats", callback_data="main:stats")],
    ]
    
    if context.user_data.get("session_token"):
        keyboard.append([InlineKeyboardButton("🚪 Logout", callback_data="main:logout")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=chat.id, text=text, reply_markup=reply_markup)
