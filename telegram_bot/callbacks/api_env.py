from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ContextTypes
from telegram_bot.config import ENVIRONMENTS_APIS


async def handle_api_env(update, context: ContextTypes.DEFAULT_TYPE):
    """Save the selected API env"""
    query = update.callback_query
    _, env_type = query.data.split(":", 1)
    
    selected_envs = [
        (env_id, env) for env_id, env in ENVIRONMENTS_APIS.items()
        if (env_type == "DEV" and not env.get("is_prod", False)) or
            (env_type == "PROD" and env.get("is_prod", False))
    ]
    
    if not selected_envs:
        await query.edit_message_text(f"❌ No {env_type} API found!")
        return
    
    env_id, env = selected_envs[0]
    
    context.user_data["api_env"] = {"id": env_id, "name": env["name"], "base_url": env["base_url"]}
    print(f"✅ API Env saved: {env['name']}")
    
    keyboard = [
        [InlineKeyboardButton("📗 GET", callback_data="api_type:GET")],
        [InlineKeyboardButton("📕 POST", callback_data="api_type:POST")],
        [InlineKeyboardButton("🏠 Dashboard", callback_data="main:dashboard")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=f"✅ API: {env['name']}\nChoose endpoint type:",
        reply_markup=reply_markup,
    )
