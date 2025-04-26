from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget

from utils.resource import internal_path


class SplashScreen(QWidget):
    finished = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 250)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)

        icon_path = internal_path("assets/logo_small.ico")
        pixmap = QPixmap(icon_path).scaled(
            64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.icon = QLabel()
        self.icon.setPixmap(pixmap)
        self.icon.setAlignment(Qt.AlignCenter)

        self.app_name = QLabel("Main and Builds")
        self.app_name.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")
        self.app_name.setAlignment(Qt.AlignCenter)

        self.label = QLabel("Carregando aplicativo...")
        self.label.setStyleSheet("font-size: 14px; color: #cccccc;")
        self.label.setAlignment(Qt.AlignCenter)

        # PROGRESSO
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(20)
        self.progress.setStyleSheet(
            """
            QProgressBar {
                background-color: #2b2b2b;
                border: 1px solid #666;
                border-radius: 10px;
            }
            QProgressBar::chunk {
                background-color: #1cc1a0;
                border-radius: 10px;
            }
        """
        )

        layout.addWidget(self.icon)
        layout.addWidget(self.app_name)
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        self.setLayout(layout)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_progress)
        self._step = 0

    def start(self):
        self._timer.start(30)

    def _update_progress(self):
        self._step += 1
        self.progress.setValue(self._step)
        if self._step >= 100:
            self._timer.stop()
            self.finished.emit()
