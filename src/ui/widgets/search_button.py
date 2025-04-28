from PySide6.QtWidgets import QPushButton


class SearchButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setText("🔍")
        self.setObjectName("btnRefreshHourAndSearch")
