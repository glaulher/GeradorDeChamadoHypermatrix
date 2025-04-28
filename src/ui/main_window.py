from functools import partial

from PySide6.QtCore import Signal
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
from ui.widgets.operator_combobox import OperatorComboBox
from ui.window_site_info import WindowSiteInfo
from utils.operator_config import load_operator_name, save_operator_name
from utils.resource import internal_path
from utils.theme_config import apply_theme, load_theme_name


class MainWindow(QMainWindow):
    operator_changed = Signal(str)

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

        self.window_control_pim = WindowControlPIM()
        self.window_dsoc = WindowDSOC()
        self.window_mb = WindowMB()
        self.window_ms = WindowMS()
        self.window_site_info = WindowSiteInfo()

        self.pages = [
            self.window_control_pim,
            self.window_dsoc,
            self.window_mb,
            self.window_ms,
            self.window_site_info,
        ]

        for page in self.pages:
            self.stack.addWidget(page)

        self.operator_label = QLabel("Analista:")
        self.operator_label.setObjectName("sidebarLabel")
        self.sidebar_layout.addWidget(self.operator_label)

        self.operator_selector = OperatorComboBox()

        saved_operator = load_operator_name()
        if saved_operator:
            self.operator_selector.setCurrentText(saved_operator)

        self.operator_widget = QWidget()
        operator_layout = QVBoxLayout(self.operator_widget)
        operator_layout.setContentsMargins(0, 0, 0, 10)  # left, top, right, bottom
        operator_layout.setSpacing(5)

        operator_layout.addWidget(self.operator_label)
        operator_layout.addWidget(self.operator_selector)

        self.sidebar_layout.addWidget(self.operator_widget)

        # Sidebar buttons
        self.button_group = QButtonGroup()
        self.button_group.setExclusive(True)
        self.sidebar_buttons = []
        button_texts = [
            "Gerador de Linhas",
            "Chamado DSOC",
            "Main Building",
            "Main Sites",
            "Pesquisa",
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

        self.operator_selector.currentIndexChanged.connect(self.save_current_operator)
        self.operator_selector.editTextChanged.connect(self.save_current_operator)

        self.operator_changed.connect(self.window_control_pim.set_operator_name)
        self.operator_changed.connect(self.window_dsoc.set_operator_name)
        self.operator_changed.connect(self.window_mb.set_operator_name)
        self.operator_changed.connect(self.window_ms.set_operator_name)

    def set_active(self, index):
        self.sidebar_buttons[index].setChecked(True)
        self.stack.setCurrentIndex(index)

    def change_theme(self, theme_name):
        apply_theme(self, theme_name)

    def save_current_operator(self, _=None):
        operator_name = self.operator_selector.currentText()
        if operator_name.strip() != "":
            save_operator_name(operator_name)
            self.operator_changed.emit(operator_name)

    def reload_operator_name(self):
        saved_operator = load_operator_name()
        if saved_operator:
            self.operator_selector.setCurrentText(saved_operator)
