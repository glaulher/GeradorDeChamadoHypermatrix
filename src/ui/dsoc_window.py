from PyQt5.QtWidgets import *
import datetime
import json
import pyperclip
from services.lookup_service import fetch_datalookup
from services.email_service import send_mail
from utils.resource import externalPath
from utils.strings import sanitize_string
from utils.datetime_utils import get_greeting

from ui.widgets.spell_check_plain_text_edit import SpellCheckPlainTextEdit
from ui.widgets.uppercase_line_edit import UpperCaseLineEdit

with open(externalPath('data/combobox_options.json'), 'r',encoding='utf-8') as file:
    combobox_options = json.load(file)

class WindowDSOC(QDialog):
    def __init__(self):
        super(WindowDSOC, self).__init__()
        self.setWindowTitle("Gerador de chamados DSOC")

        self.formGroupBox = QGroupBox("Chamados DSOC")
        self.operador_ComboBox = QComboBox()
        self.horario_LineEdit = QLineEdit()
        self.horario_LineEdit.setText(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        self.motivacao_ComboBox = QComboBox()
        self.tipo_de_alarme_ComboBox = QComboBox()
        self.gravidade_ComboBox = QComboBox()
        self.ne_name_LineEdit = UpperCaseLineEdit()
        self.causa_PlainText = SpellCheckPlainTextEdit()

        self.operador_ComboBox.addItems(combobox_options['operador'])
        self.motivacao_ComboBox.addItems(combobox_options['motivacao'])
        self.tipo_de_alarme_ComboBox.addItems(combobox_options['tipo_de_alarme'])
        self.gravidade_ComboBox.addItems(combobox_options['gravidade'])

        self.createForm()
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.getInfo)        

        subLayout = QVBoxLayout()
        subLayout.addWidget(self.formGroupBox)
        subLayout.addWidget(self.buttonBox)
        self.setLayout(subLayout)

    def getInfo(self):
        ne_name = self.ne_name_LineEdit.text()
        if fetch_datalookup('NE_NAME', ne_name, 'CLASSIFICAÇÃO') is None:
            QMessageBox.information(self, "Aviso", f"NE_NAME: {ne_name} não encontrado")
            
            return

        end_id = fetch_datalookup('NE_NAME', ne_name, 'END_ID')
        nome_do_predio = fetch_datalookup('NE_NAME', ne_name, 'NOME DO PRÉDIO')
        regional = fetch_datalookup('NE_NAME', ne_name, 'REGIONAL')
        uf = fetch_datalookup('NE_NAME', ne_name, 'UF')

        payload = {
            'Assunto': "Prezados! Solicitamos a abertura de chamado para o prédio industrial abaixo:",
            'Operador': self.operador_ComboBox.currentText(),
            'Horário': self.horario_LineEdit.text(),
            'Motivação': fetch_datalookup('END_ID', end_id, 'SUBCLASS'),
            'Alarme': self.tipo_de_alarme_ComboBox.currentText(),
            'Gravidade': self.gravidade_ComboBox.currentText(),
            'Nome do prédio': nome_do_predio,
            'NE_NAME': ne_name,
            'END_ID': end_id,
            'Regional': regional,
            'UF': uf,
            'Causa': self.causa_PlainText.toPlainText()
        }

        for k in payload:
            payload[k] = sanitize_string(payload[k])

        with open('payload.json', 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=4)

        output_str = ''
        for key in payload:
            if key == 'Assunto':
                output_str +=f"*{payload[key]}*\n\n"
            else:
                output_str +=f"*{key}*: {payload[key]}\n"
        pyperclip.copy(output_str)

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Favor verificar se o chamado está correto:\n\n{output_str}\n\n Confirma o envio do email?")
        msg.setWindowTitle("Chamado Gerado:")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if msg.exec() == QMessageBox.Yes:
            email_data = {
                "subject": f"PIM - Report | Abertura de chamado para: - {nome_do_predio} | {ne_name} - {end_id} ({regional}/{uf}) - {payload['Alarme']}",
                "greeting": get_greeting(),
                "sender_name": "Equipe PIM",
                "payload": payload
            }
            try:
                send_mail(email_data)               

                QMessageBox.information(
                    self,
                    "Sucesso",
                    "✅ E-mail enviado com sucesso!\n📋 Texto copiado para o clipboard."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erro",
                    f"❌ Erro ao enviar o e-mail.\nVerifique sua conexão e tente novamente.\n\nDetalhes técnicos:\n{str(e)}"
                )
        else:
            QMessageBox.information(
                    self,
                    "Sucesso",
                    "✅ Texto copiado para o clipboard."
                )        
        
    def createForm(self):
        layout = QFormLayout()
        layout.addRow("Operador", self.operador_ComboBox)
        layout.addRow("Horário", self.horario_LineEdit)
        layout.addRow("Motivação", self.motivacao_ComboBox)
        layout.addRow("Tipo de Alarme", self.tipo_de_alarme_ComboBox)
        layout.addRow("Gravidade", self.gravidade_ComboBox)
        layout.addRow("NE_NAME", self.ne_name_LineEdit)
        layout.addRow("Causa", self.causa_PlainText)
        self.formGroupBox.setLayout(layout)
