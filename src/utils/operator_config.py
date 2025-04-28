import json
import os

from utils.resource import external_path

CONFIG_OPERATOR_PATH = external_path("config/operator.json")


def load_operator_name():
    if not os.path.exists(CONFIG_OPERATOR_PATH):
        return ""
    try:
        with open(CONFIG_OPERATOR_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("operator", "")
    except (json.JSONDecodeError, OSError):
        return ""


def save_operator_name(operator_name):
    os.makedirs(os.path.dirname(CONFIG_OPERATOR_PATH), exist_ok=True)
    with open(CONFIG_OPERATOR_PATH, "w", encoding="utf-8") as f:
        json.dump({"operator": operator_name}, f, indent=2, ensure_ascii=False)
