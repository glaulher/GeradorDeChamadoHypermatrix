from PyQt5.QtWidgets import QMessageBox


def show_confirmation_dialog(text: str, title="Confirmação") -> bool:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(text)
    msg.setWindowTitle(title)
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    return msg.exec() == QMessageBox.Yes
