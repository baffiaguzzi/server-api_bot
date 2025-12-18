def format_server_result(r: dict) -> str:
    """Reset the server control result"""
    env_type = "PROD" if r.get("is_prod") else "DEV"
    status = r.get("status", "UNKNOWN")
    code = r.get("status_code")
    time_ms = r.get("time_ms")
    note = r.get("note", "")
    
    status_icon = "🟢" if status == "OK" else "🟡" if status == "WARN" else "🔴"
    code_str = str(code) if code is not None else "-"
    time_str = f"{time_ms:.1f} ms" if time_ms is not None else "-"
    
    lines = [
        f"[{env_type}] {r['environment']}",
        f"Result: {status_icon} {status}",
        f"HTTP: {code_str} ({time_str})",
        f"NOTE: {note}",
    ]
    return "\n".join(lines)
