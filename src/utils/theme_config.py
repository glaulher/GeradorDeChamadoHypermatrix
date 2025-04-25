import json
import os

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QComboBox, QWidget

from utils.logger import logger
from utils.resource import external_path, internal_path

CONFIG_PATH = external_path("config/theme.json")


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


def force_render_comboboxes(parent: QWidget):
    for combo in parent.findChildren(QComboBox):
        combo.repaint()

        if combo.isEditable() and combo.completer():
            popup = combo.completer().popup()
            if popup:
                popup.setStyleSheet(parent.styleSheet())


def apply_theme(parent: QWidget, theme_name: str):
    parent.setStyleSheet("")
    save_theme_name(theme_name)

    if theme_name not in ["Light", "Dark"]:
        parent.setStyleSheet("")
        return

    path = internal_path(f"styles/{theme_name}.qss")

    try:
        with open(path, "r", encoding="utf-8") as f:
            parent.setStyleSheet(f.read())
        QTimer.singleShot(0, lambda: force_render_comboboxes(parent))

    except FileNotFoundError:
        logger.error("Arquivo de estilo não encontrado: %s", path)
