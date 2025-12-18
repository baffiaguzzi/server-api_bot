from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ContextTypes
from telegram_bot.config import ENDPOINTS
from telegram_bot.services.api_service import call_api
from telegram_bot.callbacks.body import ask_body_mode


async def handle_api_flow(update, context: ContextTypes.DEFAULT_TYPE):
    """Manage the API flow: type, endpoint, language"""
    query = update.callback_query
    data = query.data or ""
    
    print(f"🔘 API Flow: {data}")  
    
    if data == "main:get_post":
        await _show_get_post_menu(query, context)
        return
    
    if data.startswith("api_type:"):
        await _show_endpoint_list(query, context)
        return
    
    if data.startswith("api_ep:"):
        await _handle_endpoint_selection(query, context)
        return
    
    if data.startswith("api_lang:"):
        await _handle_language_selection(query, context)
        return


async def _show_get_post_menu(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    """Show GET/POST menu"""
    env_info = context.user_data.get("api_env")
    if not env_info:
        await query.edit_message_text("❌ No API environment selected. Use `/endpoints`")
        return
    
    print(f"✅ Env saved: {env_info['name']}")  
    
    keyboard = [
        [InlineKeyboardButton("📗 GET endpoints", callback_data="api_type:GET")],
        [InlineKeyboardButton("📕 POST endpoints", callback_data="api_type:POST")],
        [InlineKeyboardButton("🏠 Back to dashboard", callback_data="main:dashboard")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=f"API environment: {env_info['name']}\nChoose endpoint type:",
        reply_markup=reply_markup,
    )


async def _show_endpoint_list(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    """Show the endpoint list by type"""
    ep_type = query.data.split(":", 1)[1]
    env_info = context.user_data.get("api_env")
    if not env_info:
        await query.edit_message_text("❌ No API environment. Use `/endpoints`")
        return
    
    buttons = []
    for ep_id, ep in ENDPOINTS.items():
        method = ep["method"].upper()
        if method != ep_type:
            continue
        
        needs_token = ep.get("needs_token", False)
        lock = " 🔒" if needs_token else ""
        label = f"{ep_id}) [{method}]{lock} {ep['name']}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"api_ep:{ep_id}")])
    
    buttons.extend([
        [InlineKeyboardButton("⬅️ Back to GET/POST", callback_data="main:get_post")],
        [InlineKeyboardButton("🏠 Dashboard", callback_data="main:dashboard")]
    ])
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        text=f"API env: {env_info['name']}\n📋 {ep_type} endpoints:\n🔒 = needs login",
        reply_markup=reply_markup,
    )


async def _handle_endpoint_selection(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    """Save the endpoint and manage the next flow"""
    ep_id = query.data.split(":", 1)[1]
    env_info = context.user_data.get("api_env")
    
    if not env_info:
        await query.edit_message_text("❌ No API environment selected!")
        return
    
    ep_conf = ENDPOINTS.get(ep_id)
    if not ep_conf:
        await query.edit_message_text("❌ Endpoint not found!")
        return
    
    context.user_data["api_endpoint"] = {"id": ep_id, "name": ep_conf["name"]}
    print(f"✅ Endpoint saved: {ep_conf['name']}")  
    
    if ep_conf.get("needs_token") and not context.user_data.get("session_token"):
        keyboard = [
            [InlineKeyboardButton("🔐 Login first", callback_data="api_ep:25")],
            [InlineKeyboardButton("⬅️ Back", callback_data="main:get_post")],
            [InlineKeyboardButton("🏠 Dashboard", callback_data="main:dashboard")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="⚠️ This endpoint needs login!\nGo to Login first.",
            reply_markup=reply_markup,
        )
        return
    
    method = ep_conf["method"].upper()
    
    if not ep_conf.get("needs_language"):
        token = context.user_data.get("session_token")
        if method == "GET":
            await call_api(context, query, env_info, ep_conf, language=None, token=token)
            return
        if method == "POST":
            await ask_body_mode(query, context, env_info, ep_conf)
            return
    
    keyboard = [
        [
            InlineKeyboardButton("🇮🇹 IT", callback_data="api_lang:it"),
            InlineKeyboardButton("🇬🇧 EN", callback_data="api_lang:en"),
            InlineKeyboardButton("🇪🇸 ES", callback_data="api_lang:es"),
        ],
        [InlineKeyboardButton("🏠 Back", callback_data="main:dashboard")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=f"🌐 {env_info['name']} | {ep_conf['name']}\nChoose language:",
        reply_markup=reply_markup,
    )


async def _handle_language_selection(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    """Save the language and proceed"""
    lang = query.data.split(":", 1)[1]
    env_info = context.user_data.get("api_env")
    ep_info = context.user_data.get("api_endpoint")
    
    if not all([env_info, ep_info]):
        await query.edit_message_text("❌ Missing context! Start over.")
        return
    
    context.user_data["api_language"] = lang
    print(f"✅ Language saved: {lang}") 
    
    ep_conf = ENDPOINTS[ep_info["id"]]
    method = ep_conf["method"].upper()
    path_params = ep_conf.get("path_params", [])
    
    if not ep_conf.get("needs_language"):
        token = context.user_data.get("session_token")
        if method == "GET":
            await call_api(context, query, env_info, ep_conf, language=None, token=token)
            return
        if method == "POST":
            await ask_body_mode(query, context, env_info, ep_conf)
            return
    
    if method == "GET" and path_params:
        context.user_data["awaiting_path_params"] = True
        context.user_data["path_params_keys"] = path_params
        await query.edit_message_text(
            text=f"📝 Enter path params:\n{', '.join(path_params)}\n\nExample: `value1/value2`",
            parse_mode="Markdown"
        )
        return
    
    token = context.user_data.get("session_token")
    if method == "GET":
        await call_api(context, query, env_info, ep_conf, language=lang, token=token)
        return
    
    await ask_body_mode(query, context, env_info, ep_conf)