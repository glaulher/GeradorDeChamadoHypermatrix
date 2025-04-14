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

with open(externalPath('data/combobox_options.json'), 'r', encoding='utf-8') as file:
    combobox_options = json.load(file)

class WindowMS(QDialog):
    def __init__(self):
        super(WindowMS, self).__init__()
        self.setWindowTitle("Gerador de chamados MAIN SITES")

        self.formGroupBox = QGroupBox("Chamados MAIN SITES")
        self.operador_ComboBox = QComboBox()
        self.horario_LineEdit = QLineEdit(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        self.end_id_LineEdit = UpperCaseLineEdit()
        self.tipo_de_alarme_ComboBox = QComboBox()
        self.tskeve_LineEdit = UpperCaseLineEdit()
        self.atualizacao_PlainText = SpellCheckPlainTextEdit()

        self.operador_ComboBox.addItems(combobox_options['operador'])
        self.tipo_de_alarme_ComboBox.addItems(combobox_options['tipo_de_alarme'])

        self.createForm()
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.getInfo)        

        subLayout = QVBoxLayout()
        subLayout.addWidget(self.formGroupBox)
        subLayout.addWidget(self.buttonBox)
        self.setLayout(subLayout)

    def getInfo(self):
        end_id = self.end_id_LineEdit.text()
        if fetch_datalookup('END_ID', end_id, 'CLASSIFICAÇÃO') is None:
            QMessageBox.information(self, "Aviso", f"'END_ID': {end_id} não encontrado")
            
            return

        classificacao = str(fetch_datalookup('END_ID',end_id,'SUBCLASS'))
        nome_do_predio = str(fetch_datalookup('END_ID',end_id,'NOME DO PRÉDIO'))        
        end_id = str(fetch_datalookup('END_ID',end_id,'END_ID'))
        regional = str(fetch_datalookup('END_ID',end_id,'REGIONAL'))       
        noa = ""
        uf = str(fetch_datalookup('END_ID',end_id,'UF'))
        alarme = "{0}".format(self.tipo_de_alarme_ComboBox.currentText())

        payload = {
            'Assunto':"PIM - Report Main Sites",
            'Main Site':f"{end_id} - {nome_do_predio} ({regional} / {uf})",
            'Operador':"{0}".format(self.operador_ComboBox.currentText()),
            'Horário':"{0}".format(self.horario_LineEdit.text()),
            'Class':str(fetch_datalookup('END_ID',end_id,'SUBCLASS')),
            'Alarme':alarme,
            'Tipo':str(fetch_datalookup('END_ID',end_id,'TIPO DE INFRA')),
            'Tipo de abrigo':str(fetch_datalookup('END_ID',end_id,'TIPO DE ABRIGO')),
            'Detentor':str(fetch_datalookup('END_ID',end_id,'DETENTOR DA ÁREA')),
            'TSK/EVE':"{0}".format(self.tskeve_LineEdit.text()),            
            'Atualização':"{0}".format(self.atualizacao_PlainText.toPlainText())
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
                "subject": f"PIM - Report Main Site | Main Site: {classificacao} - {nome_do_predio} | {end_id} ({regional}/{uf}) - {alarme}",
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
        layout.addRow("End_id", self.end_id_LineEdit)
        layout.addRow("Tipo de Alarme", self.tipo_de_alarme_ComboBox)
        layout.addRow("TSK / EVE", self.tskeve_LineEdit)
        layout.addRow("Atualização", self.atualizacao_PlainText)
        self.formGroupBox.setLayout(layout)
