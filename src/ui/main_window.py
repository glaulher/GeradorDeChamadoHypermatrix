from functools import partial

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ui.control_pim_window import WindowControlPIM
from ui.dsoc_window import WindowDSOC
from ui.main_building_window import WindowMB
from ui.main_sites_window import WindowMS
from utils.logger import logger
from utils.resource import internal_path
from utils.theme_config import load_theme_name, save_theme_name


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerador de Chamados")
        self.resize(1024, 768)
        self.setWindowIcon(QIcon(internal_path("assets/logo_small.ico")))

        # Sidebar
        self.sidebar = QWidget()
        with open(internal_path("styles/sidebar.qss"), "r", encoding="utf-8") as f:
            self.sidebar.setStyleSheet(f.read())
        self.sidebar.setObjectName("sidebar")
        self.sidebar_layout = QVBoxLayout()
        self.sidebar.setLayout(self.sidebar_layout)
        self.sidebar.setFixedWidth(200)

        # Stacked content
        self.stack = QStackedWidget()
        self.pages = [WindowControlPIM(), WindowDSOC(), WindowMB(), WindowMS()]

        for page in self.pages:
            self.stack.addWidget(page)

        # Sidebar buttons
        self.button_group = QButtonGroup()
        self.button_group.setExclusive(True)
        self.sidebar_buttons = []
        button_texts = [
            "Gerador de Linhas",
            "Chamado DSOC",
            "Main Building",
            "Main Sites",
        ]

        for index, text in enumerate(button_texts):
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.clicked.connect(partial(self.set_active, index))
            self.sidebar_layout.addWidget(btn)
            self.button_group.addButton(btn)
            self.sidebar_buttons.append(btn)

        self.sidebar_layout.addStretch()

        self.theme_label = QLabel("Tema:")
        self.theme_label.setObjectName("sidebarLabel")

        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["System", "Light", "Dark"])
        self.theme_selector.currentTextChanged.connect(self.change_theme)

        self.sidebar_layout.addWidget(self.theme_label)
        self.sidebar_layout.addWidget(self.theme_selector)

        load_theme = load_theme_name()

        self.theme_selector.setCurrentText(load_theme)

        # Layout principal
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Active first page
        self.set_active(0)

    def set_active(self, index):
        self.sidebar_buttons[index].setChecked(True)
        self.stack.setCurrentIndex(index)

    def change_theme(self, theme_name):
        self.setStyleSheet("")
        save_theme_name(theme_name)

        path = internal_path(f"styles/{theme_name}.qss")

        if theme_name not in ["Light", "Dark"]:
            self.setStyleSheet("")
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            logger.error("Arquivo de estilo não encontrado: %s", path)
