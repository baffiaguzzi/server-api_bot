from telegram.ext import ApplicationBuilder
from telegram_bot.config import BOT_TOKEN
from telegram_bot.commands import register_commands
from telegram_bot.callbacks.router import register_callbacks


def main():
    print("🚀 Starting bot...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    register_commands(app)
    register_callbacks(app) 
    
    print("🤖 Bot started and ready!")
    app.run_polling()

if __name__ == "__main__":
    main()