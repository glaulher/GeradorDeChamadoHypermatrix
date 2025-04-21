from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)


class ConfirmationDialog(QDialog):
    def __init__(self, text, title="Confirmação"):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(700, 500)  # Usa resize em vez de minimumSize
        self.setStyleSheet(self.dark_stylesheet())

        layout = QVBoxLayout(self)

        label = QLabel("Favor verificar se o chamado está correto:")
        label.setStyleSheet("color: white;")
        layout.addWidget(label)

        # Área de texto com scroll automático
        self.text_edit = QPlainTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(text)
        self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(
            self.text_edit, stretch=1
        )  # <-- essa linha permite expansão com scroll

        # Layout dos botões
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Confirmar")
        self.cancel_button = QPushButton("Cancelar")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def dark_stylesheet(self):
        return """
        
        QPushButton {        
            padding: 8px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #4b4f51;
        }
        QPlainTextEdit {
            
            font-family: Consolas, monospace;
            font-size: 12px;
            border: 1px solid #555;
        }
        QLabel {
        
            font-size: 14px;
        }
        """


def show_confirmation_dialog(text, title="Confirmação"):
    dialog = ConfirmationDialog(text, title)
    return dialog.exec() == QDialog.Accepted
