import json
from telegram import Update
from telegram.ext import ContextTypes
from telegram_bot.config import ENDPOINTS
from telegram_bot.services.api_service import call_api


async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles text input for JSON body and path params."""    
    if context.user_data.get("awaiting_body_json"):
        await _handle_json_body(update, context)
        return
    
    if context.user_data.get("awaiting_path_params"):
        await _handle_path_params(update, context)
        return


async def _handle_json_body(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_body_json"] = False
    
    env_info = context.user_data.get("api_env")
    ep_info = context.user_data.get("api_endpoint")
    lang = context.user_data.get("api_language")
    ep_conf = ENDPOINTS[ep_info["id"]]
    
    try:
        body = json.loads(update.message.text)
    except json.JSONDecodeError as e:
        await update.message.reply_text(f"❌ Invalid JSON: {e}\nTry again or `/start`")
        return
    
    token = context.user_data.get("session_token") if ep_conf.get("needs_token") else None
    await call_api(context, update, env_info, ep_conf, language=lang, body_override=body, token=token)


async def _handle_path_params(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_path_params"] = False
    
    env_info = context.user_data.get("api_env")
    ep_info = context.user_data.get("api_endpoint")
    lang = context.user_data.get("api_language")
    ep_conf = ENDPOINTS[ep_info["id"]]
    
    path_params_keys = context.user_data.get("path_params_keys", [])
    user_text = update.message.text.strip()
    ep_id = ep_info["id"]
    
    path_kwargs = {}
    if ep_id in ("4", "6", "11", "13", "18"):
        path_kwargs["url_path"] = user_text
    else:
        parts = [p.strip() for p in user_text.split("/") if p.strip()]
        if len(parts) != len(path_params_keys):
            await update.message.reply_text(
                f"❌ Invalid format!\nNeed {len(path_params_keys)} values with `/`: {', '.join(path_params_keys)}"
            )
            context.user_data["awaiting_path_params"] = True
            return
        
        for key, value in zip(path_params_keys, parts):
            path_kwargs[key] = value
    
    context.user_data["path_kwargs"] = path_kwargs
    
    token = context.user_data.get("session_token") if ep_conf.get("needs_token") else None
    await call_api(context, update, env_info, ep_conf, language=lang, path_kwargs=path_kwargs, token=token)
