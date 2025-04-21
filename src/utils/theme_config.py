import json
import os

from utils.resource import internal_path

CONFIG_PATH = internal_path("config/theme.json")


def load_theme_name():
    if not os.path.exists(CONFIG_PATH):
        return "System"
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("theme", "System")
    except (json.JSONDecodeError, OSError):
        return "System"


def save_theme_name(theme_name):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"theme": theme_name}, f, indent=2)
