from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt,QStringListModel

import datetime
import json
from services.lookup_service import fetch_datalookup
from services.weather_service import get_weather_data
from services.email_service import send_mail
from utils.resource import externalPath
from utils.datetime_utils import get_greeting
from utils.payload_utils import gerar_payload_e_output

from ui.widgets.spell_check_plain_text_edit import SpellCheckPlainTextEdit
from ui.widgets.uppercase_line_edit import UpperCaseLineEdit
from ui.widgets.operator_combobox import OperatorComboBox
from ui.widgets.combobox_options import load_combobox_options


with open(externalPath('data/combobox_options.json'), 'r',encoding='utf-8') as file:
    combobox_options = json.load(file)

class WindowControlePIM(QDialog): 
    def __init__(self):
        super(WindowControlePIM, self).__init__()
        self.setWindowTitle("Gerador de texto")

        self.formGroupBox = QGroupBox("Infraestrutura Hypermatrix")
        
        self.operador_ComboBox = OperatorComboBox()        
        
        self.end_id_LineEdit = UpperCaseLineEdit()
        self.tipo_de_alarme_ComboBox = QComboBox()
        self.alarmou_no_netcool_ComboBox = QComboBox()
        self.alarmou_no_servicenow_ComboBox = QComboBox()
        self.status_do_alarme_ComboBox = QComboBox()
        self.descricao_do_evento_ComboBox = QComboBox()
        self.numero_do_evento_LineEdit = UpperCaseLineEdit()
        self.observacoes_PlainText = SpellCheckPlainTextEdit()
        self.sala_de_crise_ComboBox  = QComboBox()
        self.desservico_ComboBox = QComboBox()
        self.ownertim_acionado_ComboBox = QComboBox()
        
        self.nome_owner_ComboBox = QComboBox()
        self.nome_owner_ComboBox.setEditable(True)
        self.nome_owner_ComboBox.setInsertPolicy(QComboBox.NoInsert)
        
        nome_owner_list = sorted(set([item.strip() for item in combobox_options['nome_owner']]))
        nome_owner_model = QStringListModel(nome_owner_list)

        self.nome_owner_ComboBox.addItems(nome_owner_list)

        completer = QCompleter()
        completer.setModel(nome_owner_model)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)

        self.nome_owner_ComboBox.setCompleter(completer)

        
        load_combobox_options(self.tipo_de_alarme_ComboBox, 'tipo_de_alarme')
        load_combobox_options(self.descricao_do_evento_ComboBox, 'descricao_do_evento')
        load_combobox_options(self.alarmou_no_netcool_ComboBox, 'alarmou_no_netcool')
        load_combobox_options(self.alarmou_no_servicenow_ComboBox, 'alarmou_no_servicenow')
        load_combobox_options(self.status_do_alarme_ComboBox, 'status_do_alarme')
        load_combobox_options(self.sala_de_crise_ComboBox, 'sala_de_crise')
        load_combobox_options(self.desservico_ComboBox, 'desservico')
        load_combobox_options(self.ownertim_acionado_ComboBox, 'ownertim_acionado')       
        

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
            QMessageBox.information(self, "Aviso", f"END_ID: {end_id} não encontrado")
            
            return

        latitude = fetch_datalookup('END_ID', end_id, 'latitude').replace(',', '.')
        longitude = fetch_datalookup('END_ID', end_id, 'longitude').replace(',', '.')
        
        try:
            weather_data = get_weather_data(latitude, longitude)
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro ao obter dados climáticos",
                f"❌ Não foi possível obter os dados climáticos.\n\nDetalhes: {str(e)}"
            )
            return
        
        weather = weather_data.get('current', {})

        payload = {
            'Assunto': "Abertura de chamado. Controle PIM",
            'OPERADOR': self.operador_ComboBox.currentText(),
            'DATA EVENTO': str(datetime.date.today()),
            'END_ID': end_id,
            'NE_NAME': fetch_datalookup('END_ID', end_id, 'NE NAME'),
            'CLASSIFICAÇÃO': fetch_datalookup('END_ID', end_id, 'CLASSIFICAÇÃO'),
            'TOPOLOGIA': fetch_datalookup('END_ID', end_id, 'SUBCLASS'),
            'REGIONAL': fetch_datalookup('END_ID', end_id, 'REGIONAL'),
            'TIPO DO EVENTO': self.tipo_de_alarme_ComboBox.currentText(),
            'ALARMOU NO NETCOOL': self.alarmou_no_netcool_ComboBox.currentText(),
            'ALARMOU NO SERVICENOW': self.alarmou_no_servicenow_ComboBox.currentText(),
            'STATUS DO ALARME': self.status_do_alarme_ComboBox.currentText(),
            'DESCRICAO EVENTO': self.descricao_do_evento_ComboBox.currentText(),
            'NUMERO EVENTO': self.numero_do_evento_LineEdit.text(),
            'OBSERVACOES/RECOMENDACOES': self.observacoes_PlainText.toPlainText(),
            'SALA DE CRISE?': self.sala_de_crise_ComboBox.currentText(),
            'DESSERVICO?': self.desservico_ComboBox.currentText(),
            'Owner TIM acionado?': self.ownertim_acionado_ComboBox.currentText(),
            'Nome do owner': self.nome_owner_ComboBox.currentText(),
            'NUMERO DO RELATORIO DE VULNERABILIDADE (PREENCHIMENTO EQUIPE PREVENTIVA)': '',
            'COMPORTAMENTO ESPERADO? (PREENCHIMENTO EQUIPE PREVENTIVA)': '',
            'QUAL ACAO A SER REALIZADA?(PREENCHIMENTO EQUIPE PREVENTIVA)': '',
            'STATUS ACAO(PREENCHIMENTO EQUIPE PREVENTIVA)': '',
            'TEMPO DE INTERRUPCAO AC(PREENCHIMENTO EQUIPE PREVENTIVA)': '',
            'Hora do evento': datetime.datetime.now().strftime("%H:%M:%S"),
            'Latitude': latitude,
            'Longitude': longitude,
            'Temperatura externa (°C)': str(weather.get('temperature_2m', '')),
            'Umidade (%)': str(weather.get('relative_humidity_2m', '')),
            'Velocidade do Vento (km/h)': str(weather.get('wind_speed_10m', '')),
            'Precipitação (mm)': str(weather.get('precipitation', ''))
        }

        output_str = gerar_payload_e_output(payload)

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(F"Favor verificar se o chamado está correto:\n\n{output_str}\n\n Confirma o envio do email?")
        msg.setWindowTitle("Chamado Gerado:")        
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        if msg.exec() == QMessageBox.Yes:
            email_data = {
                "subject": f"PIM - Report | Controle PIM: - {payload['NE_NAME']} | {payload['END_ID']} ({payload['REGIONAL']}) - {payload['TIPO DO EVENTO']}",
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
        layout.addRow("END_ID", self.end_id_LineEdit)
        layout.addRow("Tipo de Evento", self.tipo_de_alarme_ComboBox)
        layout.addRow("Alarmou no NetCool", self.alarmou_no_netcool_ComboBox)
        layout.addRow("Alarmou no ServiceNow", self.alarmou_no_servicenow_ComboBox)
        layout.addRow("Status do Alarme", self.status_do_alarme_ComboBox)
        layout.addRow("Descrição do evento", self.descricao_do_evento_ComboBox)
        layout.addRow("Número do evento", self.numero_do_evento_LineEdit)
        layout.addRow("Observações / Recomendações", self.observacoes_PlainText)
        layout.addRow("Sala de crise?", self.sala_de_crise_ComboBox)
        layout.addRow("Desserviço?", self.desservico_ComboBox)
        layout.addRow("OwnerTim acionado?", self.ownertim_acionado_ComboBox)
        layout.addRow("Nome Owner", self.nome_owner_ComboBox)
        self.formGroupBox.setLayout(layout)
