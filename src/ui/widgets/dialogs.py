from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from utils.resource import internal_path


class ConfirmationDialog(QDialog):
    def __init__(self, text, title="Confirmação", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)

        self.setWindowIcon(QIcon(internal_path("assets/logo_small.ico")))
        self.resize(700, 500)

        layout = QVBoxLayout(self)

        label = QLabel("Favor verificar se o chamado está correto:")

        layout.addWidget(label)

        self.text_edit = QPlainTextEdit()
        self.text_edit.setObjectName("text_dialog")
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(text)
        self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.text_edit, stretch=1)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Enviar e-mail e copiar")
        self.cancel_button = QPushButton("Apenas copiar")
        self.ok_button.setObjectName("button_dialog")
        self.cancel_button.setObjectName("button_dialog")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)


def show_confirmation_dialog(text, title="Confirmação", parent=None):
    dialog = ConfirmationDialog(text, title, parent)
    return dialog.exec() == QDialog.Accepted
