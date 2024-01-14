import validators


def validate_url(url, max_length=255):
    if not url:
        return False, 'URL обязателен'

    if len(url) > max_length:
        return False, f'URL превышает {max_length} символов'

    if not validators.url(url):
        return False, 'Некорректный URL'

    return True, None
