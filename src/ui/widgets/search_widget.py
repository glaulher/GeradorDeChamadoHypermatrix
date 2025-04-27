from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget

from ui.widgets.uppercase_line_edit import UpperCaseLineEdit


class SearchWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.line_edit = UpperCaseLineEdit()
        self.button = QPushButton("🔍")
        self.button.setObjectName("btnRefreshHourAndSearch")

        layout.addWidget(self.line_edit)
        layout.addWidget(self.button)

    def text(self):
        return self.line_edit.text()

    def set_text(self, value):
        self.line_edit.setText(value)

    def return_pressed(self, callback):
        self.line_edit.returnPressed.connect(callback)

    def clicked(self, callback):
        self.button.clicked.connect(callback)
