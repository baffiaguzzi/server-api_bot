import json
import io
from datetime import datetime
from typing import Dict, Any, Optional
from telegram import Update, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from cli.api_check import perform_request_programmatic
from telegram_bot.config import ENDPOINTS, BODY_PRESETS
from telegram_bot.utils.request_logger import log_request


async def call_api(
    context: ContextTypes.DEFAULT_TYPE,
    query: Update | CallbackQuery,
    env_info: Dict[str, Any],
    ep_conf: Dict[str, Any],
    language: Optional[str] = None,
    body_override: Optional[Dict] = None,
    token: Optional[str] = None,
    path_kwargs: Optional[Dict] = None
) -> None:
    ep_id = [k for k, v in ENDPOINTS.items() if v is ep_conf][0]

    try:
        result = perform_request_programmatic(
            base_url=env_info["base_url"],
            endpoint_id=ep_id,
            endpoint_conf=ep_conf,
            token=token,
            body_override=body_override,
            body_presets=BODY_PRESETS,
            language=language,
            path_kwargs=path_kwargs,
        )
    except Exception as e:
        print(f"❌ CLI API Error: {e}")
        result = {
            "status_code": 0,
            "status_label": "CLI_ERROR",
            "time_ms": 0,
            "error": f"CLI bug: {e}",
            "method": ep_conf.get("method", "POST"),
            "url": f"{env_info['base_url']}{ep_conf.get('path', '')}",
            "json_preview": "",
            "text_preview": "",
            "json_full": None,
        }

    user_id = query.from_user.id if isinstance(query, CallbackQuery) else query.effective_user.id
    log_request({
        "env": env_info["name"],
        "endpoint": ep_conf["name"],
        "method": result.get("method", ep_conf.get("method", "POST")),
        "url": result.get("url", f"{env_info['base_url']}{ep_conf.get('path', '')}"),
        "status_code": result.get("status_code", 0),
        "status_label": result.get("status_label", "ERR"),
        "time_ms": result.get("time_ms", 0),
        "error": result.get("error", "Unknown error"),
        "has_json": bool(result.get("json_full")),
        "user_id": user_id,
    })

    if ep_conf.get("name") == "Login" and result.get("status_code") == 200:
        session_token = result.get("session_token")
        if session_token:
            context.user_data["session_token"] = session_token

    context.user_data.pop("path_kwargs", None)

    await _format_api_response(context, query, env_info, ep_conf, result, language)


async def _format_api_response(
    context: ContextTypes.DEFAULT_TYPE,
    query: Update | CallbackQuery,
    env_info: Dict[str, Any],
    ep_conf: Dict[str, Any],
    result: Dict[str, Any],
    language: Optional[str],
):
    status = result.get("status_code", 0)
    time_ms = result.get("time_ms", 0)
    error = result.get("error")
    json_prev = result.get("json_preview") or ""
    text_prev = result.get("text_preview") or ""
    json_full = result.get("json_full")

    status_label = result.get("status_label", "ERR")
    status_icon = "🟢" if status_label == "OK" else "🟡" if status_label == "WARN" else "🔴"

    default_url = env_info["base_url"].rstrip("/") + "/" + ep_conf.get("path", "").lstrip("/")
    url = result.get("url") or default_url
    method = result.get("method") or ep_conf.get("method", "POST")

    lines = [
        f"Env: {env_info['name']}",
        f"Endpoint: {ep_conf['name']}",
        f"Language: {language or ep_conf.get('default_language', 'it')}",
        f"Method: {method}",
        f"URL: {url}",
        f"Result: {status_icon} {status_label}",
        f"Status code: {status} ({time_ms} ms)",
    ]

    if error:
        lines.append(f"Error: {error}")
    if json_prev:
        lines.append("\nJSON preview:\n" + json_prev)
    elif text_prev:
        lines.append("\nBody preview:\n" + text_prev)

    text = "\n".join(lines)

    if json_full:
        await _send_json_file(context.bot, query, json_full, ep_conf, env_info)

    keyboard = [
        [InlineKeyboardButton("⬅️ Back to GET/POST", callback_data="main:get_post")],
        [InlineKeyboardButton("📡 Change environment", callback_data="main:endpoints")],
        [InlineKeyboardButton("🏠 Dashboard", callback_data="main:dashboard")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if isinstance(query, CallbackQuery):
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        await context.bot.send_message(
            chat_id=query.effective_chat.id,
            text=text,
            reply_markup=reply_markup,
        )


async def _send_json_file(bot, query, json_data, ep_conf, env_info):
    json_bytes = json.dumps(json_data, indent=2, ensure_ascii=False).encode("utf-8")
    filename = (
        f"{ep_conf['name'].replace(' ', '_').lower()}_"
        f"{env_info['name'].lower()}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    file_obj = io.BytesIO(json_bytes)
    file_obj.name = filename

    chat_id = query.message.chat_id if isinstance(query, CallbackQuery) else query.effective_chat.id
    await bot.send_document(
        chat_id=chat_id,
        document=file_obj,
        caption="📄 Full JSON response"
    )
