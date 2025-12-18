from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram_bot.services.server_service import check_all_servers


async def server_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command `/server`: tests all environments"""
    chat = update.effective_chat
    if not chat:
        return

    text, _ = await check_all_servers()
    await context.bot.send_message(chat_id=chat.id, text=text)
