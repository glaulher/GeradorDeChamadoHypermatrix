import datetime
import json

from PyQt5.QtCore import QStringListModel, Qt
from PyQt5.QtWidgets import *

from services.diesel_service import DieselDataError, get_diesel_data
from services.email_service import send_mail
from services.lookup_service import fetch_datalookup
from ui.widgets.combobox_options import load_combobox_options
from ui.widgets.dialogs import show_confirmation_dialog
from ui.widgets.hour_widget import HourWidget
from ui.widgets.operator_combobox import OperatorComboBox
from ui.widgets.spell_check_plain_text_edit import SpellCheckPlainTextEdit
from ui.widgets.uppercase_line_edit import UpperCaseLineEdit
from utils.datetime_utils import get_greeting
from utils.payload_utils import gerar_payload_e_output
from utils.resource import externalPath


class WindowMB(QDialog):
    def __init__(self):
        super(WindowMB, self).__init__()
        self.setWindowTitle("Gerador de chamados MAIN BUILDING")

        self.formGroupBox = QGroupBox("Chamados MAIN BUILDING")

        self.operador_ComboBox = OperatorComboBox()
        self.hourWidget = HourWidget()

        self.ne_name_LineEdit = UpperCaseLineEdit()
        self.tipo_de_alarme_ComboBox = QComboBox()
        self.tipo_de_alarme_ComboBox.currentIndexChanged.connect(self.change_alarm_type)
        self.volume_diesel_LineEdit = QLineEdit()
        self.autonomia_LineEdit = QLineEdit()
        self.gmg_monitorado_ComboBox = QComboBox()
        self.tskeve_LineEdit = UpperCaseLineEdit()
        self.atualizacao_PlainText = SpellCheckPlainTextEdit()

        self.ne_name_LineEdit.textChanged.connect(self.on_ne_name_changed)

        load_combobox_options(self.tipo_de_alarme_ComboBox, "tipo_de_alarme")
        load_combobox_options(self.gmg_monitorado_ComboBox, "gmg_monitorado")

        self.createForm()
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.getInfo)

        subLayout = QVBoxLayout()
        subLayout.addWidget(self.formGroupBox)
        subLayout.addWidget(self.buttonBox)
        self.setLayout(subLayout)

    def on_ne_name_changed(self, text):
        if len(text.strip()) == 7:
            self.change_alarm_type()

    def getInfo(self):
        ne_name = self.ne_name_LineEdit.text().strip().upper()
        if fetch_datalookup("NE_NAME", ne_name, "CLASSIFICAÇÃO") is None:
            QMessageBox.information(self, "Aviso", f"NE_NAME: {ne_name} não encontrado")

            return

        classificacao = fetch_datalookup("NE_NAME", ne_name, "SUBCLASS")
        subhierarquia = fetch_datalookup("NE_NAME", ne_name, "SUBHIERARQUIA")
        nome_do_predio = fetch_datalookup("NE_NAME", ne_name, "NOME DO PRÉDIO")
        end_id = fetch_datalookup("NE_NAME", ne_name, "END_ID")
        regional = fetch_datalookup("NE_NAME", ne_name, "REGIONAL")
        uf = fetch_datalookup("NE_NAME", ne_name, "UF")
        alarme = self.tipo_de_alarme_ComboBox.currentText()

        payload = {}
        payload["Assunto"] = "PIM - Report Main Buildings"
        payload["Prédio Industrial"] = (
            f"{classificacao} {subhierarquia}- {nome_do_predio} | {ne_name} - {end_id} ({regional}/{uf})"
        )
        payload["Operador"] = "{0}".format(self.operador_ComboBox.currentText())
        payload["Horário"] = self.hourWidget.text()
        payload["Class"] = str(fetch_datalookup("END_ID", end_id, "SUBCLASS"))
        payload["Alarme"] = "{0}".format(self.tipo_de_alarme_ComboBox.currentText())

        if alarme in [
            "Falha de Energia AC",
            "GMG - Operação",
            "GMG - Defeito",
            "GMG - Nível baixo de combustível",
        ]:
            payload["Volume de Diesel (litros)"] = "{0}".format(
                self.volume_diesel_LineEdit.text()
            )
            payload["Autonomia (horas)"] = "{0}".format(self.autonomia_LineEdit.text())
            payload["GMG Monitorado"] = "{0}".format(
                self.gmg_monitorado_ComboBox.currentText()
            )

        payload["Tipo"] = str(fetch_datalookup("END_ID", end_id, "TIPO DE INFRA"))
        payload["Tipo de abrigo"] = str(
            fetch_datalookup("END_ID", end_id, "TIPO DE ABRIGO")
        )
        payload["Mantenedora"] = str(fetch_datalookup("END_ID", end_id, "MANTENEDORA"))
        payload["Tipo de atendimento"] = str(
            fetch_datalookup("END_ID", end_id, "ATENDIMENTO")
        )
        payload["TSK/EVE"] = "{0}".format(self.tskeve_LineEdit.text())
        payload["Atualização"] = "{0}".format(self.atualizacao_PlainText.toPlainText())

        output_str = gerar_payload_e_output(payload)

        confirmed = show_confirmation_dialog(
            f"Favor verificar se o chamado está correto:\n\n{output_str}\n\nConfirma o envio do email?",
            title="Chamado Gerado:",
        )

        if confirmed:
            email_data = {
                "subject": f"PIM - Report Main Building | Main Building: {classificacao} - {nome_do_predio} | {ne_name} - {end_id} ({regional}/{uf}) - {alarme}",
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
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erro",
                    f"❌ Erro ao enviar o e-mail.\nVerifique sua conexão e tente novamente.\n\nDetalhes técnicos:\n{str(e)}",
                )
        else:
            QMessageBox.information(
                self, "Sucesso", "✅ Texto copiado para o clipboard."
            )

    def change_alarm_type(self):

        alarme = self.tipo_de_alarme_ComboBox.currentText()

        is_gmg = alarme in [
            "Falha de Energia AC",
            "GMG - Operação",
            "GMG - Defeito",
            "GMG - Nível baixo de combustível",
        ]

        self.volume_diesel_LineEdit.setEnabled(is_gmg)
        self.autonomia_LineEdit.setEnabled(is_gmg)
        self.gmg_monitorado_ComboBox.setEnabled(is_gmg)

        if is_gmg:
            ne_name = self.ne_name_LineEdit.text().strip().upper()

            if not ne_name:
                QMessageBox.information(
                    self,
                    "Informação",
                    "Informe o NE Name antes de selecionar o tipo de alarme.",
                )
                return

            try:
                diesel_data = get_diesel_data(ne_name)
                self.volume_diesel_LineEdit.setText(str(diesel_data["litros"]))
                self.autonomia_LineEdit.setText(str(diesel_data["horas"]))
            except DieselDataError as e:
                QMessageBox.warning(
                    self, "Aviso", f"{str(e)}\nPreencha os dados manualmente."
                )
                self.volume_diesel_LineEdit.setText("N/D")
                self.autonomia_LineEdit.setText("N/D")
        else:
            self.volume_diesel_LineEdit.setText("")
            self.autonomia_LineEdit.setText("")

    def createForm(self):
        layout = QFormLayout()
        layout.addRow("Operador", self.operador_ComboBox)

        layout.addRow("Horário", self.hourWidget)

        layout.addRow("NE_NAME", self.ne_name_LineEdit)
        layout.addRow("Tipo de Alarme", self.tipo_de_alarme_ComboBox)
        layout.addRow("Volume de Diesel (litros)", self.volume_diesel_LineEdit)
        layout.addRow("Autonomia (horas)", self.autonomia_LineEdit)
        layout.addRow("GMG Monitorado", self.gmg_monitorado_ComboBox)
        layout.addRow("TSK / EVE", self.tskeve_LineEdit)
        layout.addRow("Atualização", self.atualizacao_PlainText)
        self.formGroupBox.setLayout(layout)
