from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLineEdit


class UpperCaseLineEdit(QLineEdit):
    focused = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textChanged.connect(self.to_upper)

    def to_upper(self, text):
        cursor = self.cursorPosition()
        self.blockSignals(True)
        self.setText(text.upper())
        self.setCursorPosition(cursor)
        self.blockSignals(False)

    # def focusInEvent(self, event):  # pylint: disable=invalid-name
    # super().focusInEvent(event)
    def mousePressEvent(self, event):
        self.clear()
        self.focused.emit()
        super().mousePressEvent(event)
