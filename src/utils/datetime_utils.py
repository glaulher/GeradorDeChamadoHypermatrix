import datetime

def get_greeting():
    hour = datetime.datetime.now().hour
    if hour < 12:
        return 'Bom dia,'
    elif 12 <= hour < 18:
        return 'Boa tarde,'
    else:
        return 'Boa noite,'

