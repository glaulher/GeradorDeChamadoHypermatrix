import datetime
import json

from PySide6.QtCore import QStringListModel, Qt, QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QCompleter,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from services.email_service import send_mail
from services.lookup_service import fetch_datalookup
from services.weather_service import get_weather_data
from ui.widgets.combobox_options import load_combobox_options
from ui.widgets.dialogs import show_confirmation_dialog
from ui.widgets.operator_combobox import OperatorComboBox
from ui.widgets.spell_check_plain_text_edit import SpellCheckPlainTextEdit
from ui.widgets.uppercase_line_edit import UpperCaseLineEdit
from utils.datetime_utils import get_greeting
from utils.payload_utils import payload_and_output
from utils.resource import external_path


class WindowControlPIM(QWidget):
    def __init__(self):
        super(WindowControlPIM, self).__init__()
        self.setWindowTitle("Gerador de texto")

        self.form_groupbox = QGroupBox("Infraestrutura Hypermatrix")

        self.operator_combobox = OperatorComboBox()

        self.site_id_line_edit = UpperCaseLineEdit()
        self.site_id_line_edit.focused.connect(self.on_site_id_focus)

        self.alarm_type_combobox = QComboBox()
        self.netcool_combobox = QComboBox()
        self.servicenow_combobox = QComboBox()
        self.alarm_status_combobox = QComboBox()
        self.event_combobox = QComboBox()
        self.event_number_line_edit = UpperCaseLineEdit()
        self.update_plain_text = SpellCheckPlainTextEdit()
        self.link_line_edit = QLineEdit()

        self.war_room_combobox = QComboBox()
        self.unavailability_combobox = QComboBox()
        self.ownertim_triggered_combobox = QComboBox()

        self.owner_name_combobox = QComboBox()
        self.owner_name_combobox.setEditable(True)
        self.owner_name_combobox.setInsertPolicy(QComboBox.NoInsert)

        # Lazy load
        QTimer.singleShot(0, self.load_date)

        self.create_form()
        self.buttonbox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonbox.accepted.connect(self.get_info)

        self.success_label = QLabel("✅ E-mail enviado! Texto copiado!")
        self.success_label.setStyleSheet("color: green; font-weight: bold;")
        self.success_label.hide()

        sublayout = QVBoxLayout()
        sublayout.addWidget(self.form_groupbox)
        sublayout.addWidget(self.success_label)
        sublayout.addWidget(self.buttonbox)
        self.setLayout(sublayout)

    def load_date(self):
        with open(
            external_path("data/combobox_options.json"), "r", encoding="utf-8"
        ) as file:
            combobox_options = json.load(file)

        nome_owner_list = sorted(
            set([item.strip() for item in combobox_options["nome_owner"]])
        )

        nome_owner_model = QStringListModel(nome_owner_list)

        self.owner_name_combobox.addItems(nome_owner_list)

        completer = QCompleter()
        completer.setModel(nome_owner_model)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)

        self.owner_name_combobox.setCompleter(completer)

        load_combobox_options(self.alarm_type_combobox, "tipo_de_alarme")
        load_combobox_options(self.event_combobox, "descricao_do_evento")
        load_combobox_options(self.netcool_combobox, "alarmou_no_netcool")
        load_combobox_options(self.servicenow_combobox, "alarmou_no_servicenow")
        load_combobox_options(self.alarm_status_combobox, "status_do_alarme")
        load_combobox_options(self.war_room_combobox, "sala_de_crise")
        load_combobox_options(self.unavailability_combobox, "desservico")
        load_combobox_options(self.ownertim_triggered_combobox, "ownertim_acionado")

    def set_operator_name(self, name: str):

        index = self.operator_combobox.findText(name)
        if index != -1:
            self.operator_combobox.setCurrentIndex(index)
        else:
            self.operator_combobox.addItem(name)
            self.operator_combobox.setCurrentText(name)

    def on_site_id_focus(self):
        self.success_label.hide()
        self.site_id_line_edit.clear()

    def get_info(self):
        site_id = self.site_id_line_edit.text()
        if len(site_id) == 7:
            site_name = "NE_NAME"
            if fetch_datalookup("NE_NAME", site_id, "CLASSIFICAÇÃO") is None:
                QMessageBox.information(
                    self, "Aviso", f"NE_NAME: {site_id} não encontrado"
                )

                return
        else:
            site_name = "END_ID"
            if fetch_datalookup("END_ID", site_id, "CLASSIFICAÇÃO") is None:
                QMessageBox.information(
                    self, "Aviso", f"END_ID: {site_id} não encontrado"
                )

                return

        latitude = fetch_datalookup(site_name, site_id, "latitude").replace(",", ".")
        longitude = fetch_datalookup(site_name, site_id, "longitude").replace(",", ".")

        try:
            weather_data = get_weather_data(latitude, longitude)

        except Exception as e:  # pylint: disable=broad-exception-caught
            QMessageBox.critical(
                self,
                "Erro ao obter dados climáticos",
                f"❌ Não foi possível obter os dados climáticos.\n\nDetalhes: {str(e)}",
            )
            return

        weather = weather_data.get("current", {})

        if len(site_id) == 7:
            # Case NE_NAME
            actual_end_id = fetch_datalookup("NE_NAME", site_id, "END_ID")
            ne_name = site_id
            classificacao = fetch_datalookup("NE_NAME", site_id, "CLASSIFICAÇÃO")
            topologia = fetch_datalookup("NE_NAME", site_id, "SUBCLASS")
            regional = fetch_datalookup("NE_NAME", site_id, "REGIONAL")
        else:
            # Case END_ID
            actual_end_id = site_id
            ne_name = fetch_datalookup("END_ID", site_id, "NE NAME")
            classificacao = fetch_datalookup("END_ID", site_id, "CLASSIFICAÇÃO")
            topologia = fetch_datalookup("END_ID", site_id, "SUBCLASS")
            regional = fetch_datalookup("END_ID", site_id, "REGIONAL")

        payload = {
            "Assunto": "Abertura de chamado. Controle PIM",
            "OPERADOR": self.operator_combobox.currentText(),
            "DATA EVENTO": str(datetime.date.today()),
            "END_ID": actual_end_id,
            "NE_NAME": ne_name,
            "CLASSIFICAÇÃO": classificacao,
            "TOPOLOGIA": topologia,
            "REGIONAL": regional,
            "TIPO DO EVENTO": self.alarm_type_combobox.currentText(),
            "ALARMOU NO NETCOOL": self.netcool_combobox.currentText(),
            "ALARMOU NO SERVICENOW": self.servicenow_combobox.currentText(),
            "STATUS DO ALARME": self.alarm_status_combobox.currentText(),
            "DESCRICAO EVENTO": self.event_combobox.currentText(),
            "NUMERO EVENTO": self.event_number_line_edit.text(),
            "OBSERVACOES/RECOMENDACOES": self.update_plain_text.toPlainText(),
            "Link": self.link_line_edit.text(),
            "SALA DE CRISE?": self.war_room_combobox.currentText(),
            "DESSERVICO?": self.unavailability_combobox.currentText(),
            "Owner TIM acionado?": self.ownertim_triggered_combobox.currentText(),
            "Nome do owner": self.owner_name_combobox.currentText(),
            "NUMERO DO RELATORIO DE VULNERABILIDADE (PREENCHIMENTO EQUIPE PREVENTIVA)": "",
            "COMPORTAMENTO ESPERADO? (PREENCHIMENTO EQUIPE PREVENTIVA)": "",
            "QUAL ACAO A SER REALIZADA?(PREENCHIMENTO EQUIPE PREVENTIVA)": "",
            "STATUS ACAO(PREENCHIMENTO EQUIPE PREVENTIVA)": "",
            "TEMPO DE INTERRUPCAO AC(PREENCHIMENTO EQUIPE PREVENTIVA)": "",
            "Hora do evento": datetime.datetime.now().strftime("%H:%M:%S"),
            "Latitude": latitude,
            "Longitude": longitude,
            "Temperatura externa (°C)": str(weather.get("temperature_2m", "")),
            "Umidade (%)": str(weather.get("relative_humidity_2m", "")),
            "Velocidade do Vento (km/h)": str(weather.get("wind_speed_10m", "")),
            "Precipitação (mm)": str(weather.get("precipitation", "")),
        }

        output_str = payload_and_output(payload)

        confirmed = show_confirmation_dialog(
            f"{output_str}", title="Chamado Gerado", parent=self
        )

        if confirmed:
            email_data = {
                "subject": (
                    f"PIM - Report | Controle PIM: - {payload['NE_NAME']} | "
                    f"{payload['END_ID']} ({payload['REGIONAL']}) - {payload['TIPO DO EVENTO']}"
                ),
                "greeting": get_greeting(),
                "sender_name": "Equipe PIM",
                "payload": payload,
            }
            try:
                send_mail(email_data)
                self.success_label.show()

            except Exception as e:  # pylint: disable=broad-exception-caught
                QMessageBox.critical(
                    self,
                    "Erro",
                    (
                        f"❌ Erro ao enviar o e-mail.\nVerifique sua conexão e tente novamente.\n\n"
                        f"Detalhes técnicos:\n{str(e)}"
                    ),
                )
        else:
            self.success_label.setText("✅ Texto copiado!")
            self.success_label.show()

    def create_form(self):
        layout = QFormLayout()

        layout.addRow("End Id ou Ne Name", self.site_id_line_edit)
        layout.addRow("Tipo de Evento", self.alarm_type_combobox)
        layout.addRow("Alarmou no NetCool", self.netcool_combobox)
        layout.addRow("Alarmou no ServiceNow", self.servicenow_combobox)
        layout.addRow("Status do Alarme", self.alarm_status_combobox)
        layout.addRow("Descrição do evento", self.event_combobox)
        layout.addRow("Número do evento", self.event_number_line_edit)
        layout.addRow("Observações / Recomendações", self.update_plain_text)
        layout.addRow("Link do gráfico", self.link_line_edit)
        layout.addRow("Sala de crise?", self.war_room_combobox)
        layout.addRow("Desserviço?", self.unavailability_combobox)
        layout.addRow("OwnerTim acionado?", self.ownertim_triggered_combobox)
        layout.addRow("Nome Owner", self.owner_name_combobox)
        self.form_groupbox.setLayout(layout)
