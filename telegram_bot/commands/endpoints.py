from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def endpoints(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command `/endpoints`: show API env"""
    chat = update.effective_chat
    if not chat:
        return
    
    text = "Choose the environment to test your endpoints:"
    
    keyboard = [
        [
            InlineKeyboardButton("🟦 DEV API", callback_data="api_env:DEV"),
            InlineKeyboardButton("🟧 PROD API", callback_data="api_env:PROD"),
        ],
        [InlineKeyboardButton("🏠 Back to the dashboard", callback_data="main:dashboard")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(chat_id=chat.id, text=text, reply_markup=reply_markup)
