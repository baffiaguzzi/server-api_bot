from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command `/logout`: remove the session token"""
    had_token = "session_token" in context.user_data
    context.user_data.pop("session_token", None)
    
    chat = update.effective_chat
    if not chat:
        return
    
    text = (
        "You've been disconnected. Session token has been removed."
        if had_token
        else "You're not authenticated (no session token found)."
    )
    
    keyboard = [
        [InlineKeyboardButton("🔐 Go to the Login", callback_data="api_ep:25")],
        [InlineKeyboardButton("📡 Endpoints", callback_data="main:endpoints")],
        [InlineKeyboardButton("🏠 Dashboard", callback_data="main:dashboard")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(chat_id=chat.id, text=text, reply_markup=reply_markup)
