from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

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
from utils.payload_utils import payload_and_output


class WindowMB(QWidget):

    GMG_ALARMS = {
        "Falha de Energia AC",
        "GMG - Operação",
        "GMG - Defeito",
        "GMG - Nível baixo de combustível",
    }

    def __init__(self):
        super(WindowMB, self).__init__()
        self.setWindowTitle("Gerador de chamados MAIN BUILDING")

        self.form_groupbox = QGroupBox("Chamados MAIN BUILDING")

        self.operator_combobox = OperatorComboBox()
        self.hour_widget = HourWidget()

        self.ne_name_line_edit = UpperCaseLineEdit(clear_on_click=True)
        self.ne_name_line_edit.focused.connect(self.on_site_id_focus)

        self.alarm_type_combobox = QComboBox()
        self.alarm_type_combobox.currentIndexChanged.connect(self.change_alarm_type)
        self.tskeve_line_edit = UpperCaseLineEdit(clear_on_click=False)
        self.update_plain_text = SpellCheckPlainTextEdit()

        # extra fields
        self.volume_diesel_line_edit = QLineEdit()
        self.autonomy_line_edit = QLineEdit()
        self.gmg_monitor_combobox = QComboBox()
        self.label_volume = QLabel("Volume de Diesel (litros)")
        self.label_autonomy = QLabel("Autonomia (horas)")
        self.label_monitor = QLabel("GMG Monitorado")

        self._setup_extra_fields()
        self._hide_fields()
        self.alarm_type_entry = False

        self.ne_name_line_edit.textChanged.connect(self.on_ne_name_changed)

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

        self.last_searched_ne_name = ""

    def _setup_extra_fields(self):
        self._extra_fields = [
            self.volume_diesel_line_edit,
            self.autonomy_line_edit,
            self.gmg_monitor_combobox,
            self.label_volume,
            self.label_autonomy,
            self.label_monitor,
        ]

    def _set_fields_visibility(self, visible: bool):
        for widget in self._extra_fields:
            widget.setVisible(visible)
        self.alarm_type_entry = visible

    def _hide_fields(self):
        self._set_fields_visibility(False)
        self.alarm_type_entry = False

        self.volume_diesel_line_edit.clear()
        self.autonomy_line_edit.clear()

    def _show_fields(self):
        self._set_fields_visibility(True)

    def _lock_fields(self):
        self.volume_diesel_line_edit.setReadOnly(True)
        self.autonomy_line_edit.setReadOnly(True)

    def _unlock_fields(self):
        self.volume_diesel_line_edit.setReadOnly(False)
        self.autonomy_line_edit.setReadOnly(False)

    def change_alarm_type(self):

        alarme = self.alarm_type_combobox.currentText()

        is_gmg = alarme in self.GMG_ALARMS

        if is_gmg:
            self._show_fields()

            ne_name = self.ne_name_line_edit.text().strip().upper()

            if not ne_name:
                self._hide_fields()
                QMessageBox.information(
                    self,
                    "Informação",
                    "Informe o NE Name antes de selecionar o tipo de alarme.",
                )
                return
            if ne_name != self.last_searched_ne_name:
                try:
                    diesel_data = get_diesel_data(ne_name)
                    self.volume_diesel_line_edit.setText(str(diesel_data["litros"]))
                    self.autonomy_line_edit.setText(str(diesel_data["horas"]))
                    self.last_searched_ne_name = ne_name
                    self._lock_fields()
                except DieselDataError as e:
                    QMessageBox.warning(
                        self, "Aviso", f"{str(e)}\nPreencha os dados manualmente."
                    )
                    self.volume_diesel_line_edit.setText("N/D")
                    self.autonomy_line_edit.setText("N/D")
                    self._unlock_fields()
        else:
            self._hide_fields()

    def load_date(self):
        load_combobox_options(self.alarm_type_combobox, "tipo_de_alarme")
        load_combobox_options(self.gmg_monitor_combobox, "gmg_monitorado")

    def set_operator_name(self, name: str):

        index = self.operator_combobox.findText(name)
        if index != -1:
            self.operator_combobox.setCurrentIndex(index)
        else:
            self.operator_combobox.addItem(name)
            self.operator_combobox.setCurrentText(name)

    def on_ne_name_changed(self, text):
        if len(text.strip()) == 7:
            self.change_alarm_type()

    def on_site_id_focus(self):
        self.success_label.hide()
        self.ne_name_line_edit.clear()
        self._hide_fields()

    def get_info(self):
        ne_name = self.ne_name_line_edit.text().strip().upper()
        if fetch_datalookup("NE_NAME", ne_name, "CLASSIFICAÇÃO") is None:
            QMessageBox.information(self, "Aviso", f"NE_NAME: {ne_name} não encontrado")

            return

        classificacao = fetch_datalookup("NE_NAME", ne_name, "SUBCLASS")
        subhierarquia = fetch_datalookup("NE_NAME", ne_name, "SUBHIERARQUIA")
        nome_do_predio = fetch_datalookup("NE_NAME", ne_name, "NOME DO PRÉDIO")
        end_id = fetch_datalookup("NE_NAME", ne_name, "END_ID")
        regional = fetch_datalookup("NE_NAME", ne_name, "REGIONAL")
        uf = fetch_datalookup("NE_NAME", ne_name, "UF")
        alarme = self.alarm_type_combobox.currentText()

        payload = {}
        payload["Assunto"] = "PIM - Report Main Buildings"
        payload["Prédio Industrial"] = (
            f"{classificacao} {subhierarquia}- {nome_do_predio} | {ne_name} - {end_id} ({regional}/{uf})"
        )
        payload["Operador"] = f"{self.operator_combobox.currentText()}"
        payload["Horário"] = self.hour_widget.text()
        payload["Class"] = str(fetch_datalookup("END_ID", end_id, "SUBCLASS"))
        payload["Alarme"] = f"{self.alarm_type_combobox.currentText()}"

        if self.alarm_type_entry:
            payload["Volume de Diesel (litros)"] = (
                f"{ self.volume_diesel_line_edit.text()}"
            )
            payload["Autonomia (horas)"] = f"{self.autonomy_line_edit.text()}"
            payload["GMG Monitorado"] = f"{self.gmg_monitor_combobox.currentText()}"

        payload["Tipo"] = str(fetch_datalookup("END_ID", end_id, "TIPO DE INFRA"))
        payload["Tipo de abrigo"] = str(
            fetch_datalookup("END_ID", end_id, "TIPO DE ABRIGO")
        )
        payload["Mantenedora"] = str(fetch_datalookup("END_ID", end_id, "MANTENEDORA"))
        payload["Tipo de atendimento"] = str(
            fetch_datalookup("END_ID", end_id, "ATENDIMENTO")
        )
        payload["TSK/EVE"] = f"{self.tskeve_line_edit.text()}"
        payload["Atualização"] = f"{self.update_plain_text.toPlainText()}"

        output_str = payload_and_output(payload)

        confirmed = show_confirmation_dialog(
            f"{output_str}", title="Chamado Gerado", parent=self
        )

        if confirmed:
            email_data = {
                "subject": (
                    f"PIM - Report Main Building | Main Building: {classificacao} - {nome_do_predio} | "
                    f"{ne_name} - {end_id} ({regional}/{uf}) - {alarme}"
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

        layout.addRow("Ne Name", self.ne_name_line_edit)
        layout.addRow("Tipo de Alarme", self.alarm_type_combobox)
        layout.addRow(self.label_volume, self.volume_diesel_line_edit)
        layout.addRow(self.label_autonomy, self.autonomy_line_edit)
        layout.addRow(self.label_monitor, self.gmg_monitor_combobox)
        layout.addRow("TSK / EVE", self.tskeve_line_edit)
        layout.addRow("Atualização", self.update_plain_text)
        self.form_groupbox.setLayout(layout)
