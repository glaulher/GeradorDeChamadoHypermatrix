from PyQt5.QtWidgets import QLineEdit

class UpperCaseLineEdit(QLineEdit):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.textChanged.connect(self.to_upper)

  def to_upper(self, text):
    cursor = self.cursorPosition()
    self.blockSignals(True)
    self.setText(text.upper())
    self.setCursorPosition(cursor)
    self.blockSignals(False)
