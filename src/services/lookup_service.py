import pandas as pd


def fetch_datalookup(search_key, search_term, return_col):
    datalookup = pd.read_csv(
        "data/datalookup.csv", sep=";", quotechar='"', encoding="utf-8", dtype={9: str}
    )
    column_map = {"NE_NAME": "NE NAME", "END_ID": "END_ID"}
    column = column_map.get(search_key, search_key)

    df_filtered = datalookup[datalookup[column] == search_term]
    try:
        value = str(df_filtered[return_col].values[0])
        return None if value == "nan" else value
    except IndexError:
        return None
