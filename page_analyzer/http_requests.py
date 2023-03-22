import requests


def make_request(url):
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException:
        response = None
    return response
