import os

import pandas as pd
import requests

from utils.resource import load_env_file

load_env_file()


class MainSiteDataError(Exception):
    pass


def get_main_site_info(end_id: str):
    try:
        sheet_id = os.getenv("SHEET_ID")
        gid_main_site = os.getenv("GID_MAIN_SITE")

        url_main_site = (
            f"https://docs.google.com/spreadsheets/d/"
            f"{sheet_id}/export?format=csv&gid={gid_main_site}"
        )

        desired_columns = [
            "END_ID",
            "ELEMENTO DE REDE",
            "CONDIÇÃO MONITORAMENTO",
            "NOME DO PRÉDIO",
            "SUB CLASS",
            "TIPOLOGIA TRANSPORTE",
            "CLASSIFICAÇÃO",
            "REGIONAL",
            "UF",
            "Testes Programados GMG",
            "CLASSIFICAÇÃO GSBI",
            "Owner",
        ]

        df_main_site = pd.read_csv(url_main_site, usecols=desired_columns)

        main_site_row = df_main_site[df_main_site["END_ID"] == end_id]

        if main_site_row.empty:
            raise MainSiteDataError(f"END_ID '{end_id}' não encontrado.")

        main_site_info = main_site_row.iloc[0].to_dict()

        return main_site_info

    except requests.ConnectionError as error:
        raise MainSiteDataError(
            "Erro de conexão ao acessar o Google Sheets."
        ) from error
    except requests.HTTPError as error:
        raise MainSiteDataError(
            f"Erro HTTP ao acessar o Google Sheets: {error.response.status_code}"
        ) from error
    except Exception as error:
        raise MainSiteDataError(
            f"Erro inesperado ao obter os dados do prédio: {error}"
        ) from error
