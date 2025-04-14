import pandas as pd
import requests
import os

from utils.resource import loadEnvFile

loadEnvFile()

class DieselDataError(Exception):    
    pass

def get_diesel_data(ne_name: str):
    try:
        
        sheet_id = os.getenv('SHEET_ID')
        gid_main_building = os.getenv('GID_MAIN_BUILDING')
        gid_controle_diesel = os.getenv('GID_CONTROLE_DIESEL')
        
        
        url_main_building = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid_main_building}'
        url_controle_diesel = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid_controle_diesel}'

        df_main_building = pd.read_csv(url_main_building, usecols=['NE_NAME', 'END_ID'])
        df_controle_diesel = pd.read_csv(url_controle_diesel, usecols=[
            'Endereço',
            'VOLUME EXISTENTE ATUAL\n (Litros)',
            'AUTONOMIA COM O VOLUME ATUAL\n (horas)'
        ])

        end_id_row = df_main_building[df_main_building['NE_NAME'] == ne_name]
        if end_id_row.empty:
            raise DieselDataError(f"NE_NAME '{ne_name}' não encontrado na aba 'Main Building'.")

        end_id = end_id_row.iloc[0]['END_ID']

        diesel_row = df_controle_diesel[df_controle_diesel['Endereço'] == end_id]
        if diesel_row.empty:
            raise DieselDataError(f"END_ID '{end_id}' não encontrado na aba 'Controle Diesel'.")

        litros = diesel_row.iloc[0]['VOLUME EXISTENTE ATUAL\n (Litros)']
        horas = diesel_row.iloc[0]['AUTONOMIA COM O VOLUME ATUAL\n (horas)']

        return {'litros': litros, 'horas': horas}

    except requests.ConnectionError as error:
        raise DieselDataError("Erro de conexão ao acessar o Google Sheets.") from error
    except requests.HTTPError as error:
        raise DieselDataError(f"Erro HTTP ao acessar o Google Sheets: {error.response.status_code}") from error
    except Exception as error:
        raise DieselDataError(f"Erro inesperado ao obter os dados de diesel: {error}") from error
