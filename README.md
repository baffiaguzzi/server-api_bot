# REST API Smoke Test – Telegram Bot

![Python](https://img.shields.io/badge/python-3.10+-blue)
![Bot](https://img.shields.io/badge/type-Telegram%20Bot-blueviolet)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-1.2.0-blue)

*A config‑driven Telegram bot (and CLI) to smoke‑test REST APIs directly from chat. Supports environments, auth/token reuse, dynamic path params, JSON bodies, request history and export.*

---

## ⚡ Highlights

* **Config‑driven**: APIs, environments and bodies live in JSON — zero code changes.
* **Telegram UI**: inline menus for env, endpoints, params and bodies.
* **Auth‑aware**: login endpoint + automatic Bearer token reuse.
* **Dynamic params**: fill `{language}`, `{id}`, `{category}` interactively.
* **Readable output**: status, timing, compact JSON preview.
* **History & export**: request logs + CSV/JSON export.
* **CLI included**: same configs, usable headless.

---

## ❓ Why not Postman?

While Postman is great for manual testing, this bot shines when:

🟢 Telegram-first – test APIs directly in chat, no app switching.

⚡ Lightweight & portable – works anywhere Python runs, no GUI needed.

📝 Config-driven – define APIs once in JSON, shareable & reusable.

🔐 Session & token management – automatic login and Bearer token reuse.

🎯 Interactive params – dynamic placeholders {id}, {category}, etc., handled inline.

📊 History & export – logs and exports built-in.

🖥️ CLI ready – perfect for headless or CI pipelines.

If your team is on Telegram, you get instant API checks with minimal setup. Postman can’t ping your API while you’re in a meeting. 😉

---

## 🚀 Quick start

```bash
git clone <repo-url>
cd server-api_bot
pip install -r requirements.txt

# start bot
start_bot.bat
# or
python -m telegram_bot.telegram_bot
```

1. Put your **BOT_TOKEN** in `telegram_bot/config.py` or via env var.
2. Open Telegram → `/start`.
3. Select config → environment → endpoint → params/body → result.

---

## 📁 Project structure

```bash
server-api_bot/
├── LICENSE
├── README.md
├── cli
│   ├── __init__.py
│   ├── api_check.py
│   └── server_check.py
├── configs
│   ├── __init__.py
│   ├── config_apis.json
│   └── config_servers.json
├── logs
├── requirements.txt
├── start_bot.bat
└── telegram_bot
    ├── __init__.py
    ├── callbacks
    │   ├── __init__.py
    │   ├── api_env.py
    │   ├── api_flow.py
    │   ├── body.py
    │   ├── router.py
    │   └── server.py
    ├── commands
    │   ├── __init__.py
    │   ├── endpoints.py
    │   ├── export.py
    │   ├── history.py
    │   ├── logout.py
    │   ├── server.py
    │   ├── stats.py
    │   └── start.py
    ├── config.py
    ├── services
    │   ├── __init__.py
    │   ├── api_service.py
    │   ├── auth_service.py
    │   └── server_service.py
    ├── telegram_bot.py
    ├── text_handler.py
    └── utils
        ├── __init__.py
        ├── formatting.py
        ├── log_reader.py
        └── request_logger.py
```

---

## ⚙️ Configuration files (`configs/*.json`)

Each API config contains **environments**, **endpoints** and optional **body_presets**.

```json
{
  "environments": {
    "1": { "name": "DEV",  "base_url": "http://dev/api/" },
    "2": { "name": "PROD", "base_url": "http://prod/api/", "is_prod": true }
  },
  "endpoints": {
    "1": {
      "name": "Category",
      "method": "GET",
      "path": "category/{id}",
      "path_params": ["id"],
      "needs_language": false
    },
    "2": {
      "name": "Login",
      "method": "POST",
      "path": "login",
      "needs_body": true,
      "needs_token": false
    }
  },
  "body_presets": {
    "2": {
      "example": {
        "username": "demo@example.com",
        "password": "password"
      }
    }
  }
}
```

### Environments

* `name`: label shown in Telegram
* `base_url`: API base URL
* `is_prod` (optional): used by server health checks

### Endpoints

* `method`: `GET` or `POST`
* `path`: relative path, supports placeholders
* `path_params`: ordered list of placeholders to ask the user
* `needs_language`: enables language selection
* `needs_body`: prompts JSON body (POST)
* `needs_token`: enforces Bearer token usage

### Body presets

Optional default JSON bodies for POST endpoints. Users can confirm or override.

---

## 🤖 Bot flow (high level)

1. `/start` → dashboard
2. Select **API config**
3. Choose **environment** (DEV/PROD)
4. Choose **GET / POST**
5. Select **endpoint**
6. Fill **language / path params / body**
7. Execute request → **summary + actions**

---

## 🧾 History & export

* `/history` → last requests (method, URL, status, timing)
* `/export` → download log file (CSV/JSON)

Logs are stored locally under `/logs`.

---

## 🖥️ CLI usage (optional)

The CLI tools reuse the same JSON configs:

```bash
python cli/api_check.py
python cli/server_check.py
```

Useful for CI or quick terminal checks without Telegram.

---

## 🔐 Security notes

* **Never commit real secrets** in public repos.
* Tokens are stored **in memory only** for the session lifetime.
* Logs should not include sensitive payloads in shared environments.

---

## 📜 License

MIT License © 2025 Gabriele A. Tambellini  
See the [LICENSE](LICENSE) file for details.
