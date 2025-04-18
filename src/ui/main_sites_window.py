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
from utils.payload_utils import payload_and_output


class WindowMS(QDialog):
    def __init__(self):
        super(WindowMS, self).__init__()
        self.setWindowTitle("Gerador de chamados MAIN SITES")

        self.form_group_box = QGroupBox("Chamados MAIN SITES")

        self.operator_combobox = OperatorComboBox()
        self.hour_widget = HourWidget()

        self.end_id_line_edit = UpperCaseLineEdit()
        self.alarm_type_combobox = QComboBox()
        self.tskeve_line_edit = UpperCaseLineEdit()
        self.update_plain_text = SpellCheckPlainTextEdit()

        load_combobox_options(self.alarm_type_combobox, "tipo_de_alarme")

        self.create_form()
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        self.button_box.accepted.connect(self.get_info)

        sub_layout = QVBoxLayout()
        sub_layout.addWidget(self.form_group_box)
        sub_layout.addWidget(self.button_box)
        self.setLayout(sub_layout)

    def get_info(self):
        end_id = self.end_id_line_edit.text()
        if fetch_datalookup("END_ID", end_id, "CLASSIFICAÇÃO") is None:
            QMessageBox.information(self, "Aviso", f"'END_ID': {end_id} não encontrado")

            return

        classificacao = str(fetch_datalookup("END_ID", end_id, "SUBCLASS"))
        nome_do_predio = str(fetch_datalookup("END_ID", end_id, "NOME DO PRÉDIO"))
        end_id = str(fetch_datalookup("END_ID", end_id, "END_ID"))
        regional = str(fetch_datalookup("END_ID", end_id, "REGIONAL"))
        uf = str(fetch_datalookup("END_ID", end_id, "UF"))
        alarme = f"{self.alarm_type_combobox.currentText()}"

        payload = {
            "Assunto": "PIM - Report Main Sites",
            "Main Site": f"{end_id} - {nome_do_predio} ({regional} / {uf})",
            "Operador": f"{self.operator_combobox.currentText()}",
            "Horário": self.hour_widget.text(),
            "Class": str(fetch_datalookup("END_ID", end_id, "SUBCLASS")),
            "Alarme": alarme,
            "Tipo": str(fetch_datalookup("END_ID", end_id, "TIPO DE INFRA")),
            "Tipo de abrigo": str(fetch_datalookup("END_ID", end_id, "TIPO DE ABRIGO")),
            "Detentor": str(fetch_datalookup("END_ID", end_id, "DETENTOR DA ÁREA")),
            "TSK/EVE": f"{self.tskeve_line_edit.text()}",
            "Atualização": f"{self.update_plain_text.toPlainText()}",
        }

        output_str = payload_and_output(payload)

        confirmed = show_confirmation_dialog(
            f"Favor verificar se o chamado está correto:\n\n{output_str}\n\nConfirma o envio do email?",
            title="Chamado Gerado:",
        )

        if confirmed:
            email_data = {
                "subject": (
                    f"PIM - Report Main Site | Main Site: {classificacao} - {nome_do_predio} | "
                    f"{end_id} ({regional}/{uf}) - {alarme}"
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

        layout.addRow("End_id", self.end_id_line_edit)
        layout.addRow("Tipo de Alarme", self.alarm_type_combobox)
        layout.addRow("TSK / EVE", self.tskeve_line_edit)
        layout.addRow("Atualização", self.update_plain_text)
        self.form_group_box.setLayout(layout)
