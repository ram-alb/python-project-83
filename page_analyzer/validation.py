import validators


def validate_url(url, max_length=255):
    if not url:
        return 'URL обязателен'

    if len(url) > max_length:
        return f'URL превышает {max_length} символов'

    if not validators.url(url):
        return 'Некорректный URL'

    return None
