from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
import datetime

class HourWidget(QWidget):
  def __init__(self, parent=None):
    super().__init__(parent)
    self.layout = QHBoxLayout(self)
    self.line_edit = QLineEdit(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    
    self.button = QPushButton("🔄")
    self.button.setFixedWidth(30)
    self.button.clicked.connect(self.atualizar_horario)

    self.layout.addWidget(self.line_edit)
    self.layout.addWidget(self.button)
    self.layout.setContentsMargins(0, 0, 0, 0)

  def atualizar_horario(self):
    self.line_edit.setText(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))

  def text(self):
    return self.line_edit.text()

  def setText(self, value: str):
    self.line_edit.setText(value)
