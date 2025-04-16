
from PyQt5.QtWidgets import QComboBox, QCompleter
from PyQt5.QtCore import Qt, QStringListModel
import json
from utils.resource import externalPath
from ui.widgets.combobox_options import load_combobox_options

class OperatorComboBox(QComboBox):
  def __init__(self, parent=None):
    super().__init__(parent)
    self.setEditable(True)
    self.setInsertPolicy(QComboBox.NoInsert)

    
    combobox_options = load_combobox_options(self, 'operador')

    operador_list = sorted(set(item.strip() for item in combobox_options.get('operador', [])))
    self.addItems(operador_list)

    model = QStringListModel(operador_list)
    completer = QCompleter()
    completer.setModel(model)
    completer.setCompletionMode(QCompleter.PopupCompletion)
    completer.setFilterMode(Qt.MatchContains)
    completer.setCaseSensitivity(Qt.CaseInsensitive)

    self.setCompleter(completer)