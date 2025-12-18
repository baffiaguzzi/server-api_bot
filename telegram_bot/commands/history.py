from telegram import Update
from telegram.ext import ContextTypes
from telegram_bot.utils.log_reader import read_latest_logs


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command `/history`: show the last API calls"""
    logs = read_latest_logs(limit=5)
    
    if not logs:
        await update.message.reply_text("📭 No request history yet..")
        return
    
    lines = ["🕘 *Last API calls:*"]
    for entry in logs:
        lines.append(
            f"• `{entry['timestamp']}`\n"
            f"  `{entry['method']} {entry['url']}`\n"
            f"  → {entry['status_code']} ({entry['time_ms']} ms)"
        )
    
    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown"
    )