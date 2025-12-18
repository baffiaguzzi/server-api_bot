from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.utils.log_reader import compute_stats_for_month


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command `/stats`: show the current monthly stats"""
    now = datetime.now()
    stats = compute_stats_for_month(now.year, now.month)

    total = stats["total_requests"]
    if total == 0:
        await update.message.reply_text("📭 No requests logged for this month yet.")
        return

    lines = [
        f"📊 *API stats for {now.year}-{now.month:02d}*",
        f"Total requests: *{total}*",
        "",
        "*Per endpoint:*",
    ]

    per_ep = stats["per_endpoint"]
    for ep_name, info in sorted(per_ep.items(), key=lambda x: x[1]["count"], reverse=True):
        count = info["count"]
        ok = info["ok"]
        warn = info["warn"]
        err = info["err"]
        avg = info["total_time_ms"] / count if count else 0
        lines.append(
            f"• *{ep_name}*\n"
            f"  Requests: {count}  |  OK: {ok}  WARN: {warn}  ERR: {err}\n"
            f"  Avg time: {avg:.1f} ms"
        )

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown"
    )
