from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QMessageBox,
    QVBoxLayout,
)

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


class WindowDSOC(QDialog):
    def __init__(self):
        super(WindowDSOC, self).__init__()
        self.setWindowTitle("Gerador de chamados DSOC")

        self.form_groupbox = QGroupBox("Chamados DSOC")

        self.operator_combobox = OperatorComboBox()
        self.hour_widget = HourWidget()

        self.motivation_combobox = QComboBox()
        self.alarm_type_combobox = QComboBox()
        self.gravity_combobox = QComboBox()
        self.ne_name_line_edit = UpperCaseLineEdit()
        self.update_plain_text = SpellCheckPlainTextEdit()

        load_combobox_options(self.motivation_combobox, "motivacao")
        load_combobox_options(self.alarm_type_combobox, "tipo_de_alarme")
        load_combobox_options(self.gravity_combobox, "gravidade")

        self.create_form()
        self.buttonbox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonbox.accepted.connect(self.get_info)

        sublayout = QVBoxLayout()
        sublayout.addWidget(self.form_groupbox)
        sublayout.addWidget(self.buttonbox)
        self.setLayout(sublayout)

    def get_info(self):
        ne_name = self.ne_name_line_edit.text()
        if fetch_datalookup("NE_NAME", ne_name, "CLASSIFICAÇÃO") is None:
            QMessageBox.information(self, "Aviso", f"NE_NAME: {ne_name} não encontrado")

            return

        end_id = fetch_datalookup("NE_NAME", ne_name, "END_ID")
        nome_do_predio = fetch_datalookup("NE_NAME", ne_name, "NOME DO PRÉDIO")
        regional = fetch_datalookup("NE_NAME", ne_name, "REGIONAL")
        uf = fetch_datalookup("NE_NAME", ne_name, "UF")

        payload = {
            "Assunto": "Prezados! Solicitamos a abertura de chamado para o prédio industrial abaixo:",
            "Operador": self.operator_combobox.currentText(),
            "Horário": self.hour_widget.text(),
            "Motivação": fetch_datalookup("END_ID", end_id, "SUBCLASS"),
            "Alarme": self.alarm_type_combobox.currentText(),
            "Gravidade": self.gravity_combobox.currentText(),
            "Nome do prédio": nome_do_predio,
            "NE_NAME": ne_name,
            "END_ID": end_id,
            "Regional": regional,
            "UF": uf,
            "Causa": self.update_plain_text.toPlainText(),
        }

        output_str = gerar_payload_e_output(payload)

        confirmed = show_confirmation_dialog(
            f"Favor verificar se o chamado está correto:\n\n{output_str}\n\nConfirma o envio do email?",
            title="Chamado Gerado:",
        )

        if confirmed:
            email_data = {
                "subject": (
                    f"PIM - Report | Abertura de chamado para: - {nome_do_predio} | "
                    f"{ne_name} - {end_id} ({regional}/{uf}) - {payload['Alarme']}"
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

        layout.addRow("Horário", self.hour_widget)

        layout.addRow("Motivação", self.motivation_combobox)
        layout.addRow("Tipo de Alarme", self.alarm_type_combobox)
        layout.addRow("Gravidade", self.gravity_combobox)
        layout.addRow("NE_NAME", self.ne_name_line_edit)
        layout.addRow("Causa", self.update_plain_text)
        self.form_groupbox.setLayout(layout)
