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
            "Resp. Green",
        ]

        df_main_building = pd.read_csv(url_main_building, usecols=desired_columns)

        building_row = df_main_building[df_main_building["NE_NAME"] == ne_name]
        if building_row.empty:
            raise BuildingDataError(f"NE_NAME '{ne_name}' não encontrado.")

        building_info = building_row.iloc[0].to_dict()

        building_region = building_info.get("REGIONAL", "").strip()
        maintainer = building_info.get("Resp. Green", "").strip()

        try:
            collaborators_on_duty = get_today_on_duty_collaborators()
            collaborators = get_collaborators()
            find_maintainer = []

            for collab in collaborators:
                region = [r.strip() for r in collab.get("Regional", "").split("/")]
                enterprise = collab.get("Empresa", "")
                name = collab.get("Colaborador", "")
                phone = collab.get("Telefone", "")

                if building_region not in region:
                    continue

                if enterprise == "Owner Tim":
                    building_info["Colaborador Tim"] = name
                    building_info["Contato Tim"] = phone
                elif name == maintainer:
                    building_info["Colaborador Terceira 1"] = name
                    building_info["Contato Terceira 1"] = phone
                    break
                else:
                    find_maintainer.append((name, phone))

            if "Colaborador Terceira 1" not in building_info:
                for i, (name, phone) in enumerate(find_maintainer[:2], start=1):
                    building_info[f"Colaborador Terceira {i}"] = name
                    building_info[f"Contato Terceira {i}"] = phone

            for colab in collaborators_on_duty:
                region_list = [
                    r.strip() for r in colab.get("Plantão Regionais", "").split("/")
                ]
                if building_region in region_list:
                    building_info["Colaborador Plantão"] = colab.get("Colaborador", "")
                    building_info["Contato Plantão"] = colab.get("Contato", "")
                    break

        except Exception as e:
            raise BuildingDataError(f"Erro ao buscar dados: {e}") from e

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


def get_collaborators():
    try:
        sheet_id = os.getenv("SHEET_ID")
        gid_collaborator = os.getenv("GID_COLLABORATOR_MAIN_BUILDING")

        url_on_collaborator = (
            f"https://docs.google.com/spreadsheets/d/"
            f"{sheet_id}/export?format=csv&gid={gid_collaborator}"
        )

        collaborators = pd.read_csv(
            url_on_collaborator,
            usecols=["Colaborador", "Empresa", "Regional", "Telefone"],
        ).to_dict(orient="records")

        return collaborators

    except Exception as error:
        raise BuildingDataError(f"Erro ao obter dados: {error}") from error


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
