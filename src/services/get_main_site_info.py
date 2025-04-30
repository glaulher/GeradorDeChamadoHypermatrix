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
        ]

        df_main_site = pd.read_csv(url_main_site, usecols=desired_columns)

        main_site_row = df_main_site[df_main_site["END_ID"] == end_id]

        if main_site_row.empty:
            raise MainSiteDataError(f"END_ID '{end_id}' não encontrado.")

        main_site_info = main_site_row.iloc[0].to_dict()
        main_site_region = main_site_info.get("REGIONAL", "").strip()

        try:

            collaborators = get_collaborators()

            for collab in collaborators:
                region = collab.get("Regional", "")
                enterprise = collab.get("Empresa", "")
                name = collab.get("Colaborador", "")
                phone = collab.get("Telefone", "")
                hour = collab.get("Horario", "")

                if main_site_region not in region:
                    continue

                if enterprise == "Owner Tim":
                    main_site_info["Colaborador"] = name
                    main_site_info["Telefone"] = phone
                    main_site_info["Horario"] = hour

                if enterprise == "Gerente":
                    main_site_info["ColaboradorGerente"] = name
                    main_site_info["TelefoneGerente"] = phone
                    main_site_info["HorarioGerente"] = hour
                    break

        except Exception as e:
            raise MainSiteDataError(f"Erro ao buscar dados: {e}") from e

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


def get_collaborators():
    try:
        sheet_id = os.getenv("SHEET_ID")
        gid_collaborator = os.getenv("GID_COLLABORATOR_MAIN_SITE")

        url_on_collaborator = (
            f"https://docs.google.com/spreadsheets/d/"
            f"{sheet_id}/export?format=csv&gid={gid_collaborator}"
        )

        collaborators = pd.read_csv(
            url_on_collaborator,
            usecols=["Colaborador", "Empresa", "Regional", "Telefone", "Horario"],
        ).to_dict(orient="records")

        return collaborators

    except Exception as error:
        raise MainSiteDataError(f"Erro ao obter dados: {error}") from error
