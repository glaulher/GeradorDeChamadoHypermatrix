import datetime
import json

from PySide6.QtCore import QStringListModel, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QCompleter,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QMessageBox,
    QVBoxLayout,
)

from services.email_service import send_mail
from services.lookup_service import fetch_datalookup
from services.weather_service import get_weather_data
from ui.widgets.combobox_options import load_combobox_options
from ui.widgets.confirmation_dialog import show_confirmation_dialog
from ui.widgets.operator_combobox import OperatorComboBox
from ui.widgets.spell_check_plain_text_edit import SpellCheckPlainTextEdit
from ui.widgets.uppercase_line_edit import UpperCaseLineEdit
from utils.datetime_utils import get_greeting
from utils.payload_utils import payload_and_output
from utils.resource import external_path

with open(external_path("data/combobox_options.json"), "r", encoding="utf-8") as file:
    combobox_options = json.load(file)


class WindowControlPIM(QDialog):
    def __init__(self):
        super(WindowControlPIM, self).__init__()
        self.setWindowTitle("Gerador de texto")

        self.form_groupbox = QGroupBox("Infraestrutura Hypermatrix")

        self.operator_combobox = OperatorComboBox()

        self.end_id_line_edit = UpperCaseLineEdit()
        self.alarm_type_combobox = QComboBox()
        self.netcool_combobox = QComboBox()
        self.servicenow_combobox = QComboBox()
        self.alarm_status_combobox = QComboBox()
        self.event_combobox = QComboBox()
        self.event_number_line_edit = UpperCaseLineEdit()
        self.update_plain_text = SpellCheckPlainTextEdit()

        self.war_room_combobox = QComboBox()
        self.unavailability_combobox = QComboBox()
        self.ownertim_triggered_combobox = QComboBox()

        self.owner_name_combobox = QComboBox()
        self.owner_name_combobox.setEditable(True)
        self.owner_name_combobox.setInsertPolicy(QComboBox.NoInsert)

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

        self.create_form()
        self.buttonbox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonbox.accepted.connect(self.get_info)

        sublayout = QVBoxLayout()
        sublayout.addWidget(self.form_groupbox)
        sublayout.addWidget(self.buttonbox)
        self.setLayout(sublayout)

    def get_info(self):
        end_id = self.end_id_line_edit.text()
        if fetch_datalookup("END_ID", end_id, "CLASSIFICAÇÃO") is None:
            QMessageBox.information(self, "Aviso", f"END_ID: {end_id} não encontrado")

            return

        latitude = fetch_datalookup("END_ID", end_id, "latitude").replace(",", ".")
        longitude = fetch_datalookup("END_ID", end_id, "longitude").replace(",", ".")

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

        payload = {
            "Assunto": "Abertura de chamado. Controle PIM",
            "OPERADOR": self.operator_combobox.currentText(),
            "DATA EVENTO": str(datetime.date.today()),
            "END_ID": end_id,
            "NE_NAME": fetch_datalookup("END_ID", end_id, "NE NAME"),
            "CLASSIFICAÇÃO": fetch_datalookup("END_ID", end_id, "CLASSIFICAÇÃO"),
            "TOPOLOGIA": fetch_datalookup("END_ID", end_id, "SUBCLASS"),
            "REGIONAL": fetch_datalookup("END_ID", end_id, "REGIONAL"),
            "TIPO DO EVENTO": self.alarm_type_combobox.currentText(),
            "ALARMOU NO NETCOOL": self.netcool_combobox.currentText(),
            "ALARMOU NO SERVICENOW": self.servicenow_combobox.currentText(),
            "STATUS DO ALARME": self.alarm_status_combobox.currentText(),
            "DESCRICAO EVENTO": self.event_combobox.currentText(),
            "NUMERO EVENTO": self.event_number_line_edit.text(),
            "OBSERVACOES/RECOMENDACOES": self.update_plain_text.toPlainText(),
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

        # confirmed = show_confirmation_dialog(
        #     f"Favor verificar se o chamado está correto:\n\n{output_str}\n\nConfirma o envio do email?",
        #     title="Chamado Gerado:",
        # )
        confirmed = show_confirmation_dialog(f"{output_str}", title="Chamado Gerado")

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

                QMessageBox.information(
                    self,
                    "Sucesso",
                    "✅ E-mail enviado com sucesso!\n📋 Texto copiado para o clipboard.",
                )
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
            QMessageBox.information(
                self, "Sucesso", "✅ Texto copiado para o clipboard."
            )

    def create_form(self):
        layout = QFormLayout()
        layout.addRow("Operador", self.operator_combobox)
        layout.addRow("END_ID", self.end_id_line_edit)
        layout.addRow("Tipo de Evento", self.alarm_type_combobox)
        layout.addRow("Alarmou no NetCool", self.netcool_combobox)
        layout.addRow("Alarmou no ServiceNow", self.servicenow_combobox)
        layout.addRow("Status do Alarme", self.alarm_status_combobox)
        layout.addRow("Descrição do evento", self.event_combobox)
        layout.addRow("Número do evento", self.event_number_line_edit)
        layout.addRow("Observações / Recomendações", self.update_plain_text)
        layout.addRow("Sala de crise?", self.war_room_combobox)
        layout.addRow("Desserviço?", self.unavailability_combobox)
        layout.addRow("OwnerTim acionado?", self.ownertim_triggered_combobox)
        layout.addRow("Nome Owner", self.owner_name_combobox)
        self.form_groupbox.setLayout(layout)
