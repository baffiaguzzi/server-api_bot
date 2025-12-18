from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ContextTypes
from telegram_bot.services.server_service import check_all_servers
from telegram_bot.config import ENVIRONMENTS


async def handle_server(update, context: ContextTypes.DEFAULT_TYPE): 
    """Manage the callbacks for the server (DEV/PROD)"""
    query = update.callback_query 
    data = query.data or ""
    _, env_type = data.split(":", 1)
    
    if not ENVIRONMENTS:
        await query.edit_message_text("No environment found in `config_servers.json`")
        return
    
    text, selected_envs = await check_all_servers(env_type)
    
    keyboard = [
        [
            InlineKeyboardButton("🟦 DEV", callback_data="server:DEV"),
            InlineKeyboardButton("🟧 PROD", callback_data="server:PROD"),
        ],
        [InlineKeyboardButton("🏠 Back to the dashboard", callback_data="main:dashboard")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text=text, reply_markup=reply_markup)
