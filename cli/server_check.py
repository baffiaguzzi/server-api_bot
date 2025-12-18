import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

import requests
from requests.exceptions import Timeout, ConnectionError, SSLError, RequestException
from colorama import init as colorama_init, Fore, Style

colorama_init(autoreset=True)

DEFAULT_TIMEOUT = 5 


def load_config(path: Path) -> Dict[str, Dict]:
    """Load environments only from config JSON."""
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("environments", {})


def choose_config_file() -> Path:
    base_dir = Path(__file__).parent
    json_files = sorted(p for p in base_dir.glob("*.json") if p.name.endswith(".json"))

    configs = [p for p in json_files if p.name not in ("requirements.txt",)]
    if not configs:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} No .json config file found in this folder.")
        raise SystemExit(1)

    print(f"\n{Fore.CYAN}=== Server Health Check ==={Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}=== Select config file ==={Style.RESET_ALL}")
    for idx, cfg in enumerate(configs, start=1):
        print(f"{idx}) {cfg.name}")

    while True:
        choice = input("Choose an option: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(configs):
            return configs[int(choice) - 1]
        print("Invalid choice, please try again.")


def choose_environments(environments: Dict[str, Dict]) -> List[str]:
    print(f"\n{Fore.CYAN}=== Select environments to test ==={Style.RESET_ALL}")
    for key, env in environments.items():
        print(f"{key}) {env['name']}")

    print("A) All environments")

    while True:
        choice = input("Choose an option (e.g. 1, 2 or A): ").strip().upper()
        if choice == "A":
            return list(environments.keys())
        if choice in environments:
            return [choice]
        print("Invalid choice, please try again.")


def get_roots(base_url: str) -> Dict[str, str]:
    """
    Given an API base like 'http://host/api/services/',
    return http/https roots: 'http://host/' and 'https://host/'.
    """
    parsed = urlparse(base_url)
    host = parsed.netloc
    return {
        "http": f"http://{host}/",
        "https": f"https://{host}/",
    }


def probe_url(url: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """
    Do a HEAD with fallback to GET on the given URL and return basic info.
    """
    data: Dict[str, Any] = {
        "url": url,
        "status_code": None,
        "time_ms": None,
        "ok": False,
        "note": "",
    }

    try:
        start = time.time()
        try:
            resp = requests.head(url, timeout=timeout, allow_redirects=True)
        except RequestException:
            resp = requests.get(url, timeout=timeout, allow_redirects=True)
        elapsed_ms = (time.time() - start) * 1000

        data["status_code"] = resp.status_code
        data["time_ms"] = round(elapsed_ms, 1)
        data["ok"] = 200 <= resp.status_code < 400
        data["note"] = f"HTTP {resp.status_code}"
    except Timeout:
        data["note"] = "Timeout"
    except SSLError as e:
        data["note"] = f"SSL error: {e}"
    except ConnectionError as e:
        data["note"] = f"Connection error: {e}"
    except RequestException as e:
        data["note"] = f"Request failed: {e}"

    return data


def classify_status(
    code: Optional[int],
    expected_status: Optional[int],
) -> str:
    """
    Decide final status: OK / WARN / ERR based on HTTP status only.
    """
    if code is None:
        return "ERROR"

    if expected_status is not None:
        if code == expected_status:
            return "OK"
        return "ERROR"

    if 200 <= code < 300:
        return "OK"
    if 300 <= code < 400 or code in (401, 403):
        return "WARN"
    if 400 <= code < 600:
        return "ERROR"
    return "ERROR"


def build_http_note(code: Optional[int]) -> str:
    if code is None:
        return "No HTTP response"
    if 200 <= code < 300:
        return "Server reachable (2xx)"
    if 300 <= code < 400:
        return f"Redirect ({code})"
    if code == 401:
        return "Unauthorized (401) – server up but requires auth"
    if code == 403:
        return "Forbidden (403) – server up but access denied"
    if 400 <= code < 500:
        return f"Client error ({code})"
    if 500 <= code < 600:
        return f"Server error ({code})"
    return f"Unexpected status {code}"


def check_server_health(
    base_url: str,
    env_name: str,
    is_prod: bool,
    expected_status: Optional[int] = None,
) -> Dict[str, Any]:
    roots = get_roots(base_url)
    http_root = roots["http"]
    https_root = roots["https"]

    result: Dict[str, Any] = {
        "environment": env_name,
        "is_prod": is_prod,
        "server_root": http_root,
        "status": "ERROR",
        "status_code": None,
        "time_ms": None,
        "note": "",
    }

    http_info = probe_url(http_root)
    code = http_info["status_code"]
    result["status_code"] = code
    result["time_ms"] = http_info["time_ms"]
    http_note = build_http_note(code)

    https_info = probe_url(https_root)
    https_note_parts: List[str] = []
    if https_info["status_code"] is not None:
        https_note_parts.append(f"HTTPS {https_info['status_code']}")
    else:
        https_note_parts.append(f"HTTPS {https_info['note']}")

    status = classify_status(code, expected_status)
    result["status"] = status

    combined_note = http_note
    combined_note += f" | HTTP root: {http_root}"
    combined_note += f" | {', '.join(https_note_parts)}"

    result["note"] = combined_note

    return result


def print_server_report(results: List[Dict[str, Any]]) -> None:
    print(f"\n{Fore.CYAN}=== Server Health Report ==={Style.RESET_ALL}\n")

    header = f"{'ENV':6} {'SERVER':35} {'CODE':5} {'TIME(ms)':9} {'STATUS':7} NOTE"
    print(header)
    print("-" * len(header))

    ok_count = warn_count = err_count = 0

    for r in results:
        env_name = r["environment"][:6]
        is_prod = r.get("is_prod", False)
        server = r["server_root"][:35]
        code = r["status_code"] if r["status_code"] is not None else "-"
        time_ms = f"{r['time_ms']:.1f}" if r["time_ms"] is not None else "-"
        status = r["status"]
        note = r["note"]

        if is_prod:
            env_label = f"[PROD] {env_name}"
            env_colored = f"{Fore.YELLOW}{env_label}{Style.RESET_ALL}"
        else:
            env_label = f"[DEV] {env_name}"
            env_colored = f"{Fore.CYAN}{env_label}{Style.RESET_ALL}"

        if status == "OK":
            status_str = f"{Fore.GREEN}OK{Style.RESET_ALL}"
            ok_count += 1
        elif status == "WARN":
            status_str = f"{Fore.YELLOW}WARN{Style.RESET_ALL}"
            warn_count += 1
        else:
            status_str = f"{Fore.RED}ERR{Style.RESET_ALL}"
            err_count += 1

        print(f"{env_colored:20} {server:35} {str(code):5} {time_ms:9} {status_str:7} {note}")

    print("\nSummary:")
    print(f"  {Fore.GREEN}OK{Style.RESET_ALL}   : {ok_count}")
    print(f"  {Fore.YELLOW}WARN{Style.RESET_ALL} : {warn_count}")
    print(f"  {Fore.RED}ERR{Style.RESET_ALL}  : {err_count}")



def main():
    config_path = choose_config_file()
    print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Using config: {config_path.name}")

    environments = load_config(config_path)

    env_ids = choose_environments(environments)
    if not env_ids:
        print(f"{Fore.YELLOW}[WARN]{Style.RESET_ALL} No environments selected. Exiting.")
        return

    results: List[Dict[str, Any]] = []

    for env_id in env_ids:
        env = environments[env_id]
        base_url = env["base_url"]
        env_name = env["name"]
        is_prod = bool(env.get("is_prod", False))
        expected_status = env.get("expected_status")

        print(
            f"\n{Fore.YELLOW}[INFO]{Style.RESET_ALL} "
            f"Checking server for environment: {env_name} ({base_url})"
        )

        r = check_server_health(
            base_url=base_url,
            env_name=env_name,
            is_prod=is_prod,
            expected_status=expected_status,
        )

        if r["status"] == "OK":
            print(f"{Fore.GREEN}[RESULT]{Style.RESET_ALL} Server OK ({r['status_code']}) - {r['note']}")
        elif r["status"] == "WARN":
            print(f"{Fore.YELLOW}[RESULT]{Style.RESET_ALL} Server reachable with warnings ({r['status_code']}) - {r['note']}")
        else:
            print(f"{Fore.RED}[RESULT]{Style.RESET_ALL} Server error - {r['note']}")

        results.append(r)

    print_server_report(results)


if __name__ == "__main__":
    main()
