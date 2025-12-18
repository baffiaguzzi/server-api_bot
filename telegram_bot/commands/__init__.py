from telegram.ext import Application, CommandHandler, MessageHandler, filters
from .start import start
from .server import server_all
from .endpoints import endpoints
from .logout import logout
from .history import history_command
from .export import export_command
from .stats import stats_command
from telegram_bot.text_handler import handle_text_input


def register_commands(app: Application):
    print("🔌 Registering the command handlers...") 
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("server", server_all))
    app.add_handler(CommandHandler("endpoints", endpoints))
    app.add_handler(CommandHandler("logout", logout))
    app.add_handler(CommandHandler("history", history_command))
    app.add_handler(CommandHandler("export", export_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
    print("✅ Command handlers registered!")
