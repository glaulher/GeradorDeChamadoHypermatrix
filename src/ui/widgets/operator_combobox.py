import json

from PySide6.QtCore import QStringListModel, Qt
from PySide6.QtWidgets import QComboBox, QCompleter

from utils.resource import externalPath


class OperatorComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)

        with open(
            externalPath("data/combobox_options.json"), "r", encoding="utf-8"
        ) as file:
            combobox_options = json.load(file)

        operador_list = sorted(
            set(item.strip() for item in combobox_options.get("operador", []))
        )
        self.addItems(operador_list)

        model = QStringListModel(operador_list)
        completer = QCompleter()
        completer.setModel(model)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)

        self.setCompleter(completer)
