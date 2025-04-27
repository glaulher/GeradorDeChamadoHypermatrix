import os

import pandas as pd
import requests

from utils.resource import load_env_file

load_env_file()


class BuildingDataError(Exception):
    pass


def get_main_build_info(ne_name: str):
    try:
        sheet_id = os.getenv("SHEET_ID")
        gid_main_building = os.getenv("GID_MAIN_BUILDING")

        url_main_building = (
            f"https://docs.google.com/spreadsheets/d/"
            f"{sheet_id}/export?format=csv&gid={gid_main_building}"
        )

        desired_columns = [
            "HIERARQUIA",
            "SUBHIERARQUIA",
            "NOME DO PRÉDIO",
            "NE_NAME",
            "END_ID",
            "REGIONAL",
            "UF",
            "Testes Programados GMG",
            "MANTENEDORA",
            "ATENDIMENTO",
            "LOCALIDADE",
            "OWNER RESPONSÁVEL",
            "Resp. Green",
        ]

        df_main_building = pd.read_csv(url_main_building, usecols=desired_columns)

        building_row = df_main_building[df_main_building["NE_NAME"] == ne_name]
        if building_row.empty:
            raise BuildingDataError(f"NE_NAME '{ne_name}' não encontrado.")

        building_info = building_row.iloc[0].to_dict()

        return building_info

    except requests.ConnectionError as error:
        raise BuildingDataError(
            "Erro de conexão ao acessar o Google Sheets."
        ) from error
    except requests.HTTPError as error:
        raise BuildingDataError(
            f"Erro HTTP ao acessar o Google Sheets: {error.response.status_code}"
        ) from error
    except Exception as error:
        raise BuildingDataError(
            f"Erro inesperado ao obter os dados do prédio: {error}"
        ) from error
