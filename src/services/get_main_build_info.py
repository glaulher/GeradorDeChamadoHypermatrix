import os
from datetime import datetime

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

        owner_regional = building_info.get("REGIONAL", "").strip()
        if owner_regional:
            try:
                collaborators = get_today_on_duty_collaborators()

                for collaborator in collaborators:
                    plantao_regionais = collaborator.get("Plantão Regionais", "").split(
                        "/"
                    )
                    plantao_regionais = [r.strip() for r in plantao_regionais]

                    if owner_regional in plantao_regionais:
                        building_info["Colaborador"] = collaborator.get(
                            "Colaborador", ""
                        )
                        building_info["Contato"] = collaborator.get("Contato", "")
                        break
            except Exception as error:
                raise BuildingDataError(f"Erro ao buscar plantão: {error}") from error

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


def get_today_on_duty_collaborators():
    try:
        sheet_id = os.getenv("SHEET_ID")
        gid_ordely = os.getenv("GID_ORDELY")

        url_on_duty = (
            f"https://docs.google.com/spreadsheets/d/"
            f"{sheet_id}/export?format=csv&gid={gid_ordely}"
        )

        df_on_duty = pd.read_csv(url_on_duty)

        today_day = datetime.now().day  # número do dia, ex: 27
        today_column = str(today_day)  # nome da coluna, ex: "27"

        # Filtrar linhas onde no dia atual tem "Plantão"
        filtered_df = df_on_duty[df_on_duty[today_column] == "Plantão"]

        collaborators = filtered_df[
            ["Colaborador", "Contato", "Plantão Regionais"]
        ].to_dict(orient="records")

        return collaborators

    except Exception as error:
        raise BuildingDataError(f"Erro ao obter dados de plantão: {error}") from error
