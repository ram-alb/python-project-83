import requests
from page_analyzer import db


def fake_get_url_data(id):
    class UrlData:
        id = 10
        name = 'http://someurl.com'
        created_at = '2022-03-10'
    return UrlData


def fake_get_from_url_checks(url_id):
    return [
        {
            'id': 1,
            'url_id': 10,
            'status_code': None,
            'h1': None,
            'title': None,
            'description': None,
            'created_at': '2022-04-05'
        },
        {
            'id': 2,
            'url_id': 10,
            'status_code': None,
            'h1': None,
            'title': None,
            'description': None,
            'created_at': '2023-02-20'
        },
    ]


def fake_add_data_to_url_checks(params):
    pass


def test_url_details(client, monkeypatch):
    monkeypatch.setattr(db, 'get_url_data', fake_get_url_data)
    monkeypatch.setattr(db, 'get_from_url_checks', fake_get_from_url_checks)

    response = client.get('/urls/10')

    assert response.status_code == 200
    assert '<td>10</td>' in response.text
    assert '<td>http://someurl.com</td>' in response.text
    assert '<td>1</td>' in response.text
    assert '<td>2023-02-20</td>' in response.text


def test_url_check_fail(client, monkeypatch):
    monkeypatch.setattr(db, 'add_data_to_url_checks', fake_add_data_to_url_checks)
    monkeypatch.setattr(db, 'get_url_data', fake_get_url_data)

    response = client.post('/urls/10/checks', data={})

    with client.session_transaction() as session:
        flash_message = dict(session['_flashes']).get('error')

    assert response.status_code == 302
    assert flash_message == 'Произошла ошибка при проверке'


def test_url_check_success(client, monkeypatch):
    def fake_requests_get(url):
        class Response():
            status_code = 302
            headers = {'Content-Type': 'some header'}
        return Response()

    monkeypatch.setattr(db, 'add_data_to_url_checks', fake_add_data_to_url_checks)
    monkeypatch.setattr(db, 'get_url_data', fake_get_url_data)
    monkeypatch.setattr(requests, 'get', fake_requests_get)

    response = client.post('/urls/10/checks', data={})

    with client.session_transaction() as session:
        flash_message = dict(session['_flashes']).get('success')

    assert response.status_code == 302
    assert flash_message == 'Страница успешно проверена'
