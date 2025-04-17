import requests


def get_weather_data(latitude, longitude):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        f"&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,precipitation"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except (requests.ConnectionError, requests.Timeout) as error:
        raise ConnectionError("Erro de conexão com o serviço de clima.") from error
    except requests.HTTPError as error:
        raise RuntimeError(f"Erro HTTP: {error.response.status_code}") from error
    except Exception as error:
        raise RuntimeError("Erro inesperado ao obter os dados climáticos.") from error
