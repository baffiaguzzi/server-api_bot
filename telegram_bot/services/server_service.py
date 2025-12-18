from cli.server_check import check_server_health
from telegram_bot.utils.formatting import format_server_result
from telegram_bot.config import ENVIRONMENTS


async def check_all_servers(env_type: str = None):
    """Test ALL the DEV or PROD servers"""
    results = []
    selected_envs = []
    
    for env_id, env in ENVIRONMENTS.items():
        is_prod = bool(env.get("is_prod", False))
        if env_type == "DEV" and not is_prod:
            selected_envs.append((env_id, env))
        elif env_type == "PROD" and is_prod:
            selected_envs.append((env_id, env))
    
    for env_id, env in selected_envs:
        result = check_server_health(
            base_url=env["base_url"],
            env_name=env["name"],
            is_prod=bool(env.get("is_prod", False)),
            expected_status=env.get("expected_status"),
        )
        results.append(format_server_result(result))
    
    return "\n\n".join(results), selected_envs
