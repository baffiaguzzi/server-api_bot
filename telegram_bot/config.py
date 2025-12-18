from pathlib import Path
from cli.server_check import load_config
from cli.api_check import load_config as load_api_config

CONFIG_SERVERS = (Path(__file__).parent.parent / "configs" / "config_servers.json").resolve()
ENVIRONMENTS = load_config(CONFIG_SERVERS)

CONFIG_APIS = (Path(__file__).parent.parent / "configs" / "config_apis.json").resolve()
ENVIRONMENTS_APIS, ENDPOINTS, BODY_PRESETS = load_api_config(CONFIG_APIS)


BOT_TOKEN = "..."  #your telegram bot token

BOT_NAME = 'RESTAPISmoker_Bot' #or whatever
BOT_USERNAME = 'restapismokerBot' #or whatever

COMMAND = 'python -m telegram_bot.telegram_bot'