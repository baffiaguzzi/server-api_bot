from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ContextTypes
from telegram_bot.services.api_service import call_api
from telegram_bot.config import ENDPOINTS


async def handle_body_mode(update, context: ContextTypes.DEFAULT_TYPE):
    """Manage the selection of body mode (default/custom)."""
    query = update.callback_query
    data = query.data or ""
    mode = data.split(":", 1)[1]

    print(f"🔘 Body mode: {mode}")

    env_info = context.user_data.get("api_env")
    ep_info = context.user_data.get("api_endpoint")
    lang = context.user_data.get("api_language")

    print(f"🔍 Context - env: {env_info}, ep: {ep_info}, lang: {lang}")

    if not env_info or not ep_info:
        await query.edit_message_text("❌ Missing API context! Use `/endpoints`")
        return

    ep_id = ep_info["id"]
    ep_conf = ENDPOINTS.get(ep_id)
    if not ep_conf:
        await query.edit_message_text("❌ Endpoint config not found!")
        return

    print(f"✅ Valid context: {env_info['name']} - {ep_conf['name']}")

    if ep_conf.get("needs_token") and not context.user_data.get("session_token"):
        keyboard = [
            [InlineKeyboardButton("🔐 Go to Login", callback_data="api_ep:25")],
            [InlineKeyboardButton("⬅️ Back", callback_data="main:get_post")],
            [InlineKeyboardButton("🏠 Dashboard", callback_data="main:dashboard")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="⚠️ Login required first!",
            reply_markup=reply_markup,
        )
        return

    token = context.user_data.get("session_token") if ep_conf.get("needs_token") else None

    print(f"🚀 Calling API - lang: {lang or 'default'}")

    if mode == "default":
        await call_api(
            context,
            query,
            env_info,
            ep_conf,
            language=lang,
            body_override=None,
            token=token,
        )
        return

    if mode == "custom":
        context.user_data["awaiting_body_json"] = True
        lang_text = lang or "default"
        await query.edit_message_text(
            text=(
                f"📝 *{env_info['name']}* - *{ep_conf['name']}* (lang: {lang_text})\n\n"
                "Send JSON body:\n"
                "`{\"key\": \"value\"}`"
            ),
            parse_mode="Markdown",
        )
        return


async def ask_body_mode(
    query: CallbackQuery,
    context: ContextTypes.DEFAULT_TYPE,
    env_info: dict,
    ep_conf: dict,
):
    """Show the menu for choosing the (default/custom)."""
    print(f"🔘 Asking body mode for {ep_conf['name']}")

    text = f"🌐 *{env_info['name']}*\n📡 *{ep_conf['name']}*\n\nChoose JSON body:"

    keyboard = [
        [InlineKeyboardButton("📦 Default JSON", callback_data="body_mode:default")],
        [InlineKeyboardButton("✏️ Custom JSON", callback_data="body_mode:custom")],
        [InlineKeyboardButton("🏠 Dashboard", callback_data="main:dashboard")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode="Markdown")
