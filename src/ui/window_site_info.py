import math

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractButton,
    QFormLayout,
    QGroupBox,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from services.get_main_build_info import BuildingDataError, get_main_build_info
from services.get_main_site_info import MainSiteDataError, get_main_site_info
from ui.widgets.search_widget import SearchWidget


class WindowSiteInfo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Consulta de Informações de Sites")

        self.form_groupbox = QGroupBox("Informações do Site")

        self.search_widget = SearchWidget()
        self.search_widget.return_pressed(self.fetch_info)
        self.search_widget.clicked(self.fetch_info)

        self.table_widget = QTableWidget(0, 2)
        self.table_widget.setHorizontalHeaderLabels(["Dados", "Informações"])
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectItems)
        self.table_widget.setSelectionMode(QTableWidget.MultiSelection)
        self.table_widget.horizontalHeader().setStretchLastSection(True)

        font_metrics = self.table_widget.fontMetrics()
        header_height = font_metrics.height() + 20
        self.table_widget.horizontalHeader().setFixedHeight(header_height)

        self.table_widget.verticalHeader().setFixedWidth(36)

        self.table_widget.setStyleSheet(
            """
            QTableWidget::item:selected {
                color: white;
                background-color: rgb(22, 160, 133);
            }
            
            QHeaderView::section {
                background-color: rgb(43, 62, 80);
                color: white;
            }
        """
        )

        self.create_form()

        layout = QVBoxLayout()
        layout.addWidget(self.form_groupbox)
        self.setLayout(layout)

        self.is_main_site_info = True

    def showEvent(self, event):  # pylint: disable=invalid-name
        super().showEvent(event)

        corner_button = self.table_widget.findChild(QAbstractButton)
        if corner_button:
            corner_button.setStyleSheet(
                """
                background-color: rgb(43, 62, 80);
                border: none;
            """
            )

    def create_form(self):
        form_layout = QFormLayout()
        form_layout.addRow("End Id ou Ne Name", self.search_widget)
        form_layout.addRow(self.table_widget)

        self.form_groupbox.setLayout(form_layout)

    def fetch_info(self):
        site_name = self.search_widget.text().strip()

        if len(site_name) == 7:
            try:

                site_info = get_main_build_info(site_name)
                self.is_main_site_info = False

            except BuildingDataError as e:

                QMessageBox.critical(self, "Erro", f"Erro ao buscar site: {str(e)}")
                return
        else:
            try:
                site_info = get_main_site_info(site_name)
                self.is_main_site_info = True

            except MainSiteDataError as e:

                QMessageBox.critical(self, "Erro", f"Erro ao buscar site: {str(e)}")
                return

        if not site_info:
            QMessageBox.information(
                self, "Aviso", f"NE_NAME: {site_name} não encontrado"
            )
            return

        self.populate_table(site_info)

    def populate_table(self, site_info):
        if self.is_main_site_info:
            campos = {
                "END_ID": "End Id",
                "ELEMENTO DE REDE": "Elemento De Rede",
                "CONDIÇÃO MONITORAMENTO": "Condição Monitoramento",
                "NOME DO PRÉDIO": "Nome Do Prédio",
                "SUB CLASS": "Sub Class",
                "TIPOLOGIA TRANSPORTE": "Tipologia Transporte",
                "CLASSIFICAÇÃO": "Classificação",
                "REGIONAL": "Regional",
                "UF": "UF",
                "Testes Programados GMG": "Testes Programados GMG",
                "CLASSIFICAÇÃO GSBI": "GSBI",
                "Owner": "Owner",
            }
        else:
            campos = {
                "HIERARQUIA": "Hierarquia",
                "SUBHIERARQUIA": "Subhierarquia",
                "NOME DO PRÉDIO": "Nome Do Prédio",
                "END_ID": "End Id",
                "REGIONAL": "Regional",
                "UF": "UF",
                "Testes Programados GMG": "Testes Programados GMG",
                "MANTENEDORA": "Mantenedora",
                "ATENDIMENTO": "Atendimento",
                "LOCALIDADE": "Localidade",
                "OWNER RESPONSÁVEL": "Owner Responsável",
                "Resp. Green": "Resp. Green",
            }

        self.table_widget.setRowCount(len(campos))

        for row, (key, format_name) in enumerate(campos.items()):
            item_campo = QTableWidgetItem(format_name)
            valor = site_info.get(key, "")

            if valor is None or (isinstance(valor, float) and math.isnan(valor)):
                valor = ""

            item_valor = QTableWidgetItem(str(valor))

            self.table_widget.setItem(row, 0, item_campo)
            self.table_widget.setItem(row, 1, item_valor)

        for row in range(self.table_widget.rowCount()):
            item = self.table_widget.item(row, 0)
            if item:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setForeground(QColor(22, 160, 133))

        self.table_widget.setColumnWidth(0, 220)
