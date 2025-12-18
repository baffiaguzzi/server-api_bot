import time
import requests
import json
from typing import Dict
from pathlib import Path
from colorama import init as colorama_init, Fore, Style

colorama_init(autoreset=True)

ENVIRONMENTS: Dict[str, Dict] = {}
ENDPOINTS: Dict[str, Dict] = {}
BODY_PRESETS: Dict[str, Dict] = {}

LAST_TOKEN: str | None = None
DEFAULT_TIMEOUT = 10


def load_config(path: Path):
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return (
        data.get("environments", {}),
        data.get("endpoints", {}),
        data.get("body_presets", {})
    )


def choose_from_menu(title: str, options: Dict[str, Dict]) -> str:
    while True:
        print(f"\n=== {title} ===")
        for key, data in options.items():
            print(f"{key}) {data['name']}")
        choice = input("Choose an option: ").strip()
        if choice in options:
            return choice
        print("Invalid choice, please try again.")


def choose_config_file() -> Path:
    base_dir = Path(__file__).parent
    json_files = sorted(p for p in base_dir.glob("*.json") if p.name != "__pycache__")

    configs = [p for p in json_files if p.name != "requirements.txt"]
    if not configs:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} No .json config file found in this folder.")
        raise SystemExit(1)

    print(f"\n{Fore.CYAN}=== Select config file ==={Style.RESET_ALL}")
    for idx, cfg in enumerate(configs, start=1):
        print(f"{idx}) {cfg.name}")

    while True:
        choice = input("Choose an option: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(configs):
            return configs[int(choice) - 1]
        print("Invalid choice, please try again.")


def ask_language() -> str:
    lang = input("\nInsert language (e.g. it, en, 1, 2...): ").strip()
    while not lang:
        print("Language cannot be empty.")
        lang = input("Insert language: ").strip()
    return lang


def ask_token() -> str:
    global LAST_TOKEN
    default = LAST_TOKEN or ""
    if default:
        print(f"\nToken saved from login (session_token):\n{default[:60]}...")
        token = input("Use this token? (Enter = yes, or paste another token): ").strip()
        if not token:
            return default
    else:
        token = input("\nInsert token (Bearer): ").strip()

    while not token:
        print("Token cannot be empty.")
        token = input("Insert token (Bearer): ").strip()

    LAST_TOKEN = token
    return token


def ask_body_json(endpoint_id: str) -> dict:
    preset = BODY_PRESETS.get(endpoint_id)
    if preset:
        example = preset.get("example", {})
        print("\nFound example body for this endpoint:")
        print(json.dumps(example, indent=2, ensure_ascii=False))
        use_preset = input("Use this body? (y/n) [y]: ").strip().lower() or "y"
        if use_preset == "y":
            return example

    print("\nInsert JSON body (single line) or leave empty to use {}:")
    raw = input("> ").strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON: {e}")
        print("Using empty body {}.")
        return {}


def classify_http_status(code: int | None) -> str:
    if code is None:
        return "ERR"
    if 200 <= code < 300:
        return "OK"
    if 300 <= code < 400 or code in (401, 403):
        return "WARN"
    if 400 <= code < 600:
        return "ERR"
    return "ERR"


def perform_request(base_url: str, endpoint_id: str, endpoint_conf: Dict):
    method = endpoint_conf["method"].upper()
    path = endpoint_conf["path"]

    if endpoint_conf.get("needs_language"):
        language = ask_language()
        path = path.replace("{language}", str(language).strip())

    if "{id}" in path:
        _id = input("\nInsert id: ").strip()
        path = path.replace("{id}", _id)
    if "{url_path}" in path:
        url_path = input("\nInsert url_path: ").strip()
        path = path.replace("{url_path}", url_path)
    if "{product_path}" in path:
        product_path = input("\nInsert product_path: ").strip()
        path = path.replace("{product_path}", product_path)

    if not path.startswith("/"):
        url = base_url.rstrip("/") + "/" + path
    else:
        url = base_url.rstrip("/") + path

    headers = {}
    body = None

    if endpoint_conf.get("needs_token"):
        token = ask_token()
        headers["Authorization"] = f"Bearer {token}"

    if endpoint_conf.get("needs_body") and method == "POST":
        body = ask_body_json(endpoint_id)

    print(f"\n{Fore.YELLOW}[INFO]{Style.RESET_ALL} Base URL: {base_url}")
    print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Endpoint: {endpoint_conf['name']}")
    print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Method: {method}")
    print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} URL: {url}")
    if headers:
        print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Headers: {headers}")
    if body is not None:
        print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Body: {body}")

    try:
        start = time.time()
        if method == "GET":
            response = requests.get(url, headers=headers or None, timeout=DEFAULT_TIMEOUT)
        elif method == "POST":
            response = requests.post(url, headers=headers or None, json=body, timeout=DEFAULT_TIMEOUT)
        else:
            print(f"[ERROR] HTTP method {method} is not supported yet.")
            return

        elapsed = (time.time() - start) * 1000

        print(f"\n{Fore.GREEN}[RESULT]{Style.RESET_ALL} Status code: {response.status_code}")
        print(f"{Fore.GREEN}[RESULT]{Style.RESET_ALL} Response time: {elapsed:.1f} ms")

        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            try:
                data = response.json()

                global LAST_TOKEN
                if endpoint_id == "25" and response.status_code == 200:
                    token = data.get("data", {}).get("session_token")
                    if token:
                        LAST_TOKEN = token
                        print(f"\n{Fore.CYAN}[INFO]{Style.RESET_ALL} session_token saved in memory for subsequent calls.")

                print(f"\n{Fore.GREEN}[RESULT]{Style.RESET_ALL} JSON (partial view):")
                if isinstance(data, dict):
                    for i, (k, v) in enumerate(data.items()):
                        print(f"  {k}: {str(v)[:80]}")
                        if i >= 4:
                            break
                elif isinstance(data, list):
                    print(f"  List with {len(data)} items.")
                    if data:
                        print(f"  First item: {str(data[0])[:120]}")
                else:
                    print(f"  Unexpected JSON type: {type(data)}")
            except Exception as e:
                print(f"{Fore.YELLOW}[WARN]{Style.RESET_ALL} Error while parsing JSON: {e}")
                print("Body (first 300 chars):")
                print(response.text[:300])
        else:
            print(f"\n{Fore.GREEN}[RESULT]{Style.RESET_ALL} Body (first 300 chars):")
            print(response.text[:300])

    except requests.exceptions.RequestException as e:
        print(f"\n{Fore.RED}[ERROR]{Style.RESET_ALL} Request failed: {e}")

    print(f"\n{Fore.CYAN}=== End of request ==={Style.RESET_ALL}")


def perform_request_programmatic(
    base_url: str,
    endpoint_id: str,
    endpoint_conf: Dict,
    token: str | None = None,
    body_override: dict | None = None,
    body_presets: Dict[str, Dict] | None = None,
    language: str | None = None,
    path_kwargs=None,
) -> dict:
    """
    Bot/other version: no input(), no print,
    returns only a dict with the main data.
    Default values for params (id, url_path, etc.).
    """
    method = endpoint_conf["method"].upper()
    path_template = endpoint_conf["path"]

    fmt_kwargs = dict(path_kwargs or {})
    fmt_kwargs.setdefault(
        "language",
        language or endpoint_conf.get("default_language", "it"),
    )

    try:
        path = path_template.format(**fmt_kwargs)
    except KeyError as e:
        return {
            "url": None,
            "method": method,
            "status_code": None,
            "time_ms": None,
            "json_preview": None,
            "text_preview": None,
            "error": f"Missing path param: {e}",
            "session_token": None,
            "json_full": None,
            "status_label": "ERR",
        }

    if not path.startswith("/"):
        url = base_url.rstrip("/") + "/" + path
    else:
        url = base_url.rstrip("/") + path

    headers = {}
    body = None

    if endpoint_conf.get("needs_token") and token:
        headers["Authorization"] = f"Bearer {token}"

    if endpoint_conf.get("needs_body") and method == "POST":
        presets = body_presets or BODY_PRESETS
        body = body_override if body_override is not None else presets.get(endpoint_id, {}).get("example", {})

    print("DEBUG BOT BODY:", body)

    result = {
        "url": url,
        "method": method,
        "status_code": None,
        "time_ms": None,
        "json_preview": None,
        "text_preview": None,
        "error": None,
        "session_token": None,
        "json_full": None,
    }

    try:
        start = time.time()
        if method == "GET":
            response = requests.get(url, headers=headers or None, timeout=DEFAULT_TIMEOUT)
        elif method == "POST":
            response = requests.post(url, headers=headers or None, json=body, timeout=DEFAULT_TIMEOUT)
        else:
            result["error"] = f"HTTP method {method} is not supported yet."
            result["status_label"] = "ERR"
            return result

        elapsed = (time.time() - start) * 1000
        result["status_code"] = response.status_code
        result["time_ms"] = round(elapsed, 1)

        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            try:
                data = response.json()
                result["json_full"] = data

                # Session token for login (endpoint 25)
                if endpoint_id == "25" and response.status_code == 200 and isinstance(data, dict):
                    token = data.get("data", {}).get("session_token")
                    if token:
                        result["session_token"] = token

                if isinstance(data, dict):
                    preview_items = []
                    for i, (k, v) in enumerate(data.items()):
                        preview_items.append(f"{k}: {str(v)[:80]}")
                        if i >= 4:
                            break
                    result["json_preview"] = "\n".join(preview_items)
                elif isinstance(data, list):
                    info = [f"List with {len(data)} items."]
                    if data:
                        info.append(f"First item: {str(data[0])[:120]}")
                    result["json_preview"] = "\n".join(info)
                else:
                    result["json_preview"] = f"Unexpected JSON type: {type(data)}"
            except Exception as e:
                result["error"] = f"Error while parsing JSON: {e}"
                result["text_preview"] = response.text[:300]
        else:
            result["text_preview"] = response.text[:300]

    except requests.exceptions.RequestException as e:
        result["error"] = f"Request failed: {e}"

    result["status_label"] = classify_http_status(result["status_code"])
    return result



def main():
    global ENVIRONMENTS, ENDPOINTS, BODY_PRESETS

    print(f"{Fore.CYAN}=== API quick check ==={Style.RESET_ALL}")

    config_path = choose_config_file()
    print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Using config: {config_path.name}")

    ENVIRONMENTS, ENDPOINTS, BODY_PRESETS = load_config(config_path)

    env_choice = choose_from_menu("Choose environment:", ENVIRONMENTS)
    env = ENVIRONMENTS[env_choice]
    base_url = env["base_url"]

    endpoint_choice = choose_from_menu("Choose endpoint to test:", ENDPOINTS)
    endpoint_conf = ENDPOINTS[endpoint_choice]

    perform_request(base_url, endpoint_choice, endpoint_conf)


if __name__ == "__main__":
    main()
