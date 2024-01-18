from urllib.parse import urlparse

import validators


def validate_url(url, max_length=255):
    if not url:
        return 'URL обязателен'

    if len(url) > max_length:
        return f'URL превышает {max_length} символов'

    if not validators.url(url):
        return 'Некорректный URL'

    return None


def parse_url(url_string):
    parsed_url = urlparse(url_string)
    return f'{parsed_url.scheme}://{parsed_url.netloc}'
