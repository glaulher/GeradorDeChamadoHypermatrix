from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLineEdit


class UpperCaseLineEdit(QLineEdit):
    focused = Signal()

    def __init__(self, *args, clear_on_click=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.textChanged.connect(self.to_upper)
        self.clear_on_click = clear_on_click

    def to_upper(self, text):
        cursor = self.cursorPosition()
        self.blockSignals(True)
        self.setText(text.upper())
        self.setCursorPosition(cursor)
        self.blockSignals(False)

    # def focusInEvent(self, event):  # pylint: disable=invalid-name
    # super().focusInEvent(event)
    def mousePressEvent(self, event):
        if self.clear_on_click:
            self.clear()
        self.focused.emit()
        super().mousePressEvent(event)
