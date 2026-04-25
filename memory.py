import json
import os
from datetime import datetime

DATA_DIR = "career_data"


def _safe_name(name: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)[:40]


def _profile_file(name: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"{_safe_name(name)}_profile.json")


def _log_file(name: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"{_safe_name(name)}_logs.json")


def list_profiles() -> list:
    """Return list of all profile names."""
    if not os.path.exists(DATA_DIR):
        return []
    names = []
    for f in sorted(os.listdir(DATA_DIR)):
        if f.endswith("_profile.json"):
            raw = f.replace("_profile.json", "")
            names.append(raw.replace("_", " "))
    return names


def load_profile(name: str) -> dict:
    path = _profile_file(name)
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_profile(name: str, data: dict):
    data["updated"] = str(datetime.now())
    with open(_profile_file(name), "w") as f:
        json.dump(data, f, indent=2)


def delete_profile(name: str):
    for path in [_profile_file(name), _log_file(name)]:
        if os.path.exists(path):
            os.remove(path)


def get_session_logs(name: str) -> list:
    path = _log_file(name)
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def add_session_log(name: str, session_type: str, content: str, meta: dict = None):
    """Append a session log entry."""
    logs = get_session_logs(name)
    logs.append({
        "type": session_type,
        "content": content,
        "meta": meta or {},
        "timestamp": datetime.now().isoformat()
    })
    with open(_log_file(name), "w") as f:
        json.dump(logs, f, indent=2)
