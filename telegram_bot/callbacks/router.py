from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import Application, ContextTypes, CallbackQueryHandler

from .server import handle_server
from .api_env import handle_api_env
from .api_flow import handle_api_flow
from .body import handle_body_mode
from telegram_bot.commands.logout import logout
from telegram_bot.commands.stats import stats_command


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main router for ALL the callbacks"""
    query = update.callback_query
    if not query:
        return
        
    await query.answer()
    data = query.data or ""
    
    print(f"🔘 DEBUG: Callback received: {data}")  
    
    if data == "main:dashboard":
        await _show_dashboard(query, context)
        return
    
    if data == "main:server":
        await _show_server_menu(query)
        return
    
    if data == "main:endpoints":
        await _show_endpoints_menu(query)
        return
    
    if data == "main:stats":
        fake_update = Update(
            update.update_id,
            message=query.message 
        )
        await stats_command(fake_update, context)
        return
    
    if data.startswith("server:"):
        await handle_server(update, context)
        return
    
    if data.startswith("api_env:"):
        await handle_api_env(update, context)
        return
    
    if any(data.startswith(prefix) for prefix in ["api_type:", "api_ep:", "api_lang:", "main:get_post"]):
        await handle_api_flow(update, context)
        return
    
    if data.startswith("body_mode:"):
        await handle_body_mode(update, context)
        return
    
    if data == "main:logout":
        await logout(update, context)
        return


async def _show_dashboard(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌐 Check SERVER", callback_data="main:server")],
        [InlineKeyboardButton("📡 Check ENDPOINTS", callback_data="main:endpoints")],
        [InlineKeyboardButton("📊 Stats", callback_data="main:stats")],
    ]
    
    if context.user_data.get("session_token"):
        keyboard.append([InlineKeyboardButton("🚪 Logout", callback_data="main:logout")])
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="🏠 Main Dashboard:\nChoose what you wanna do:",
        reply_markup=reply_markup,
    )


async def _show_server_menu(query: CallbackQuery):
    keyboard = [
        [
            InlineKeyboardButton("🟦 DEV", callback_data="server:DEV"),
            InlineKeyboardButton("🟧 PROD", callback_data="server:PROD"),
        ],
        [InlineKeyboardButton("🏠 Back to dashboard", callback_data="main:dashboard")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="🌐 Check SERVER:\nChoose environment:",
        reply_markup=reply_markup,
    )


async def _show_endpoints_menu(query: CallbackQuery):
    keyboard = [
        [
            InlineKeyboardButton("🟦 DEV API", callback_data="api_env:DEV"),
            InlineKeyboardButton("🟧 PROD API", callback_data="api_env:PROD"),
        ],
        [InlineKeyboardButton("🏠 Back to dashboard", callback_data="main:dashboard")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="📡 Check ENDPOINTS:\nChoose API environment:",
        reply_markup=reply_markup,
    )


def register_callbacks(app: Application):
    """Register the callback router"""
    print("🔌 Registering the callback handlers...")  
    app.add_handler(CallbackQueryHandler(callback_router))
    print("✅ Callback handlers registered!")
