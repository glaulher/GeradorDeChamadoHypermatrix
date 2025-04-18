import datetime
import json

from PyQt5.QtCore import QStringListModel, Qt
from PyQt5.QtWidgets import *

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


class WindowMS(QDialog):
    def __init__(self):
        super(WindowMS, self).__init__()
        self.setWindowTitle("Gerador de chamados MAIN SITES")

        self.formGroupBox = QGroupBox("Chamados MAIN SITES")

        self.operador_ComboBox = OperatorComboBox()
        self.hourWidget = HourWidget()

        self.end_id_LineEdit = UpperCaseLineEdit()
        self.tipo_de_alarme_ComboBox = QComboBox()
        self.tskeve_LineEdit = UpperCaseLineEdit()
        self.atualizacao_PlainText = SpellCheckPlainTextEdit()

        load_combobox_options(self.tipo_de_alarme_ComboBox, "tipo_de_alarme")

        self.createForm()
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.getInfo)

        subLayout = QVBoxLayout()
        subLayout.addWidget(self.formGroupBox)
        subLayout.addWidget(self.buttonBox)
        self.setLayout(subLayout)

    def getInfo(self):
        end_id = self.end_id_LineEdit.text()
        if fetch_datalookup("END_ID", end_id, "CLASSIFICAÇÃO") is None:
            QMessageBox.information(self, "Aviso", f"'END_ID': {end_id} não encontrado")

            return

        classificacao = str(fetch_datalookup("END_ID", end_id, "SUBCLASS"))
        nome_do_predio = str(fetch_datalookup("END_ID", end_id, "NOME DO PRÉDIO"))
        end_id = str(fetch_datalookup("END_ID", end_id, "END_ID"))
        regional = str(fetch_datalookup("END_ID", end_id, "REGIONAL"))
        noa = ""
        uf = str(fetch_datalookup("END_ID", end_id, "UF"))
        alarme = "{0}".format(self.tipo_de_alarme_ComboBox.currentText())

        payload = {
            "Assunto": "PIM - Report Main Sites",
            "Main Site": f"{end_id} - {nome_do_predio} ({regional} / {uf})",
            "Operador": "{0}".format(self.operador_ComboBox.currentText()),
            "Horário": self.hourWidget.text(),
            "Class": str(fetch_datalookup("END_ID", end_id, "SUBCLASS")),
            "Alarme": alarme,
            "Tipo": str(fetch_datalookup("END_ID", end_id, "TIPO DE INFRA")),
            "Tipo de abrigo": str(fetch_datalookup("END_ID", end_id, "TIPO DE ABRIGO")),
            "Detentor": str(fetch_datalookup("END_ID", end_id, "DETENTOR DA ÁREA")),
            "TSK/EVE": "{0}".format(self.tskeve_LineEdit.text()),
            "Atualização": "{0}".format(self.atualizacao_PlainText.toPlainText()),
        }

        output_str = gerar_payload_e_output(payload)

        confirmed = show_confirmation_dialog(
            f"Favor verificar se o chamado está correto:\n\n{output_str}\n\nConfirma o envio do email?",
            title="Chamado Gerado:",
        )

        if confirmed:
            email_data = {
                "subject": f"PIM - Report Main Site | Main Site: {classificacao} - {nome_do_predio} | {end_id} ({regional}/{uf}) - {alarme}",
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

    def createForm(self):
        layout = QFormLayout()
        layout.addRow("Operador", self.operador_ComboBox)

        layout.addRow("Horário", self.hourWidget)

        layout.addRow("End_id", self.end_id_LineEdit)
        layout.addRow("Tipo de Alarme", self.tipo_de_alarme_ComboBox)
        layout.addRow("TSK / EVE", self.tskeve_LineEdit)
        layout.addRow("Atualização", self.atualizacao_PlainText)
        self.formGroupBox.setLayout(layout)
