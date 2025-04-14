def sanitize_string(text):
    return str(text).replace('\r', '').replace('\n', '').replace('\t', '').strip()
