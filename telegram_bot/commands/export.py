from telegram import Update
from telegram.ext import ContextTypes
from telegram_bot.utils.log_reader import get_latest_logfile


async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command `/export`: export log file"""
    logfile = get_latest_logfile()
    
    if not logfile:
        await update.message.reply_text("📭 No logs to export..")
        return
    
    await context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=logfile.open("rb"),
        filename=logfile.name,
        caption="📦 API request logs"
    )