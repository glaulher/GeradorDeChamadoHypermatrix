from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QWidget,
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
from utils.operator_config import load_operator_name
from utils.payload_utils import payload_and_output


class WindowDSOC(QWidget):
    def __init__(self):
        super(WindowDSOC, self).__init__()
        self.setWindowTitle("Gerador de chamados DSOC")

        self.form_groupbox = QGroupBox("Chamados DSOC")

        self.operator_combobox = OperatorComboBox()
        self.hour_widget = HourWidget()

        self.motivation_combobox = QComboBox()
        self.alarm_type_combobox = QComboBox()
        self.gravity_combobox = QComboBox()
        self.ne_name_line_edit = UpperCaseLineEdit(clear_on_click=True)
        self.ne_name_line_edit.focused.connect(self.on_site_id_focus)

        self.update_plain_text = SpellCheckPlainTextEdit()

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

        # Lazy load
        QTimer.singleShot(0, self.load_date)

    def set_operator_name(self, name: str):

        index = self.operator_combobox.findText(name)
        if index != -1:
            self.operator_combobox.setCurrentIndex(index)
        else:
            self.operator_combobox.addItem(name)
            self.operator_combobox.setCurrentText(name)

    def load_date(self):
        load_combobox_options(self.motivation_combobox, "motivacao")
        load_combobox_options(self.alarm_type_combobox, "tipo_de_alarme")
        load_combobox_options(self.gravity_combobox, "gravidade")
        saved_operator = load_operator_name()
        if saved_operator:
            self.operator_combobox.setCurrentText(saved_operator)

    def on_site_id_focus(self):
        self.success_label.hide()
        self.ne_name_line_edit.clear()

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

        output_str = payload_and_output(payload)

        confirmed = show_confirmation_dialog(
            f"{output_str}", title="Chamado Gerado", parent=self
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

        layout.addRow("Horário", self.hour_widget)

        layout.addRow("Motivação", self.motivation_combobox)
        layout.addRow("Tipo de Alarme", self.alarm_type_combobox)
        layout.addRow("Gravidade", self.gravity_combobox)
        layout.addRow("Ne Name", self.ne_name_line_edit)
        layout.addRow("Causa", self.update_plain_text)
        self.form_groupbox.setLayout(layout)
