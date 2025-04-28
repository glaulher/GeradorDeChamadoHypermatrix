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
from utils.payload_utils import payload_and_output


class WindowMS(QWidget):
    def __init__(self):
        super(WindowMS, self).__init__()
        self.setWindowTitle("Gerador de chamados MAIN SITES")

        self.form_group_box = QGroupBox("Chamados MAIN SITES")

        self.operator_combobox = OperatorComboBox()
        self.hour_widget = HourWidget()

        self.end_id_line_edit = UpperCaseLineEdit()
        self.end_id_line_edit.focused.connect(self.on_site_id_focus)

        self.alarm_type_combobox = QComboBox()
        self.tskeve_line_edit = UpperCaseLineEdit()
        self.update_plain_text = SpellCheckPlainTextEdit()

        # extra fields to be filled in manually in case of not finding the end id
        self.regional_line_edit = UpperCaseLineEdit()
        self.uf_line_edit = UpperCaseLineEdit()
        self.classification_line_edit = UpperCaseLineEdit()
        self.building_name_line_edit = UpperCaseLineEdit()
        self.type_line_edit = UpperCaseLineEdit()
        self.shelter_type_line_edit = UpperCaseLineEdit()
        self.area_owner_line_edit = UpperCaseLineEdit()

        self.regional_line_edit.setPlaceholderText("Ex: TSDE")
        self.uf_line_edit.setPlaceholderText("Ex: MG")
        self.classification_line_edit.setPlaceholderText("Ex: POP LD")
        self.building_name_line_edit.setPlaceholderText("Ex: ITAMARANDIBA")
        self.type_line_edit.setPlaceholderText("Ex: GREENFIELD")
        self.shelter_type_line_edit.setPlaceholderText("Ex: CONTAINER")
        self.area_owner_line_edit.setPlaceholderText("Ex: AMERICAN TOWER")

        self.hypermatrix_label = QLabel()
        self.hypermatrix_label.setStyleSheet("color: red; font-weight: bold;")
        self.label_regional = QLabel("Regional (Hypermatrix)")
        self.label_uf = QLabel("UF (Hypermatrix)")
        self.label_class = QLabel("Classificação (Hypermatrix)")
        self.label_nome_predio = QLabel("Nome do Prédio (Hypermatrix)")
        self.label_tipo = QLabel("Tipo (Hypermatrix)")
        self.label_tipo_abrigo = QLabel("Tipo de Abrigo (Hypermatrix)")
        self.label_detentor = QLabel("Detentor da Área (Hypermatrix)")

        self._setup_extra_fields()
        self._hide_fields()
        self.manual_entry = False

        self.create_form()
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        self.button_box.accepted.connect(self.get_info)

        self.success_label = QLabel("✅ E-mail enviado! Texto copiado!")
        self.success_label.setStyleSheet("color: green; font-weight: bold;")
        self.success_label.hide()

        sublayout = QVBoxLayout()
        sublayout.addWidget(self.form_group_box)
        sublayout.addWidget(self.success_label)
        sublayout.addWidget(self.button_box)
        self.setLayout(sublayout)

        # Lazy load
        QTimer.singleShot(0, self.load_date)

    def load_date(self):
        load_combobox_options(self.alarm_type_combobox, "tipo_de_alarme")

    def set_operator_name(self, name: str):

        index = self.operator_combobox.findText(name)
        if index != -1:
            self.operator_combobox.setCurrentIndex(index)
        else:
            self.operator_combobox.addItem(name)
            self.operator_combobox.setCurrentText(name)

    def on_site_id_focus(self):
        self.success_label.hide()
        self.end_id_line_edit.clear()
        self._hide_fields()

    def _setup_extra_fields(self):
        self._extra_fields = [
            self.hypermatrix_label,
            self.label_regional,
            self.regional_line_edit,
            self.label_uf,
            self.uf_line_edit,
            self.label_class,
            self.classification_line_edit,
            self.label_nome_predio,
            self.building_name_line_edit,
            self.label_tipo,
            self.type_line_edit,
            self.label_tipo_abrigo,
            self.shelter_type_line_edit,
            self.label_detentor,
            self.area_owner_line_edit,
        ]

    def _set_fields_visibility(self, visible: bool):
        for widget in self._extra_fields:
            widget.setVisible(visible)

    def _hide_fields(self):
        self._set_fields_visibility(False)
        self.manual_entry = False
        self.hypermatrix_label.setText(
            "⚠️ Utilize as informações cadastradas no Hypermatrix"
        )

    def _show_fields(self):
        self._set_fields_visibility(True)

    def get_info(self):
        end_id = self.end_id_line_edit.text()

        if not self.manual_entry:

            if end_id == "":
                self.hypermatrix_label.setText("⚠️ Digite o End Id")
                self.hypermatrix_label.show()
                return

            if fetch_datalookup("END_ID", end_id, "CLASSIFICAÇÃO") is None:
                QMessageBox.information(
                    self, "Aviso", f"'END_ID': {end_id} não encontrado"
                )
                self._show_fields()
                self.manual_entry = True

                return

        self._finalize_payload(end_id)

    def _finalize_payload(self, end_id):

        if self.manual_entry:

            regional = self.regional_line_edit.text()
            uf = self.uf_line_edit.text()
            classification = self.classification_line_edit.text()
            building_name = self.building_name_line_edit.text()
            infra_type = self.type_line_edit.text()
            shelter_type = self.shelter_type_line_edit.text()
            area_owner = self.area_owner_line_edit.text()
        else:
            classification = str(fetch_datalookup("END_ID", end_id, "SUBCLASS"))
            building_name = str(fetch_datalookup("END_ID", end_id, "NOME DO PRÉDIO"))
            end_id = str(fetch_datalookup("END_ID", end_id, "END_ID"))
            regional = str(fetch_datalookup("END_ID", end_id, "REGIONAL"))
            uf = str(fetch_datalookup("END_ID", end_id, "UF"))
            infra_type = str(fetch_datalookup("END_ID", end_id, "TIPO DE INFRA"))
            shelter_type = str(fetch_datalookup("END_ID", end_id, "TIPO DE ABRIGO"))
            area_owner = str(fetch_datalookup("END_ID", end_id, "DETENTOR DA ÁREA"))

        alarme = f"{self.alarm_type_combobox.currentText()}"

        payload = {
            "Assunto": "PIM - Report Main Sites",
            "Main Site": f"{end_id} - {building_name} ({regional} / {uf})",
            "Operador": self.operator_combobox.currentText(),
            "Horário": self.hour_widget.text(),
            "Class": classification,
            "Alarme": alarme,
            "Tipo": infra_type,
            "Tipo de abrigo": shelter_type,
            "Detentor": area_owner,
            "TSK/EVE": f"{self.tskeve_line_edit.text()}",
            "Atualização": f"{self.update_plain_text.toPlainText()}",
        }

        output_str = payload_and_output(payload)

        confirmed = show_confirmation_dialog(
            f"{output_str}", title="Chamado Gerado", parent=self
        )

        if confirmed:
            email_data = {
                "subject": (
                    f"PIM - Report Main Site | Main Site: {classification} - {building_name} | "
                    f"{end_id} ({regional}/{uf}) - {alarme}"
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

        layout.addRow("End id", self.end_id_line_edit)
        layout.addRow("Tipo de Alarme", self.alarm_type_combobox)
        layout.addRow("TSK / EVE", self.tskeve_line_edit)
        layout.addRow("Atualização", self.update_plain_text)

        # hide fields
        layout.addRow(self.hypermatrix_label)
        layout.addRow(self.label_regional, self.regional_line_edit)
        layout.addRow(self.label_uf, self.uf_line_edit)
        layout.addRow(self.label_class, self.classification_line_edit)
        layout.addRow(self.label_nome_predio, self.building_name_line_edit)
        layout.addRow(self.label_tipo, self.type_line_edit)
        layout.addRow(self.label_tipo_abrigo, self.shelter_type_line_edit)
        layout.addRow(self.label_detentor, self.area_owner_line_edit)

        self.form_group_box.setLayout(layout)
