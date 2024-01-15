import requests
from page_analyzer import db


def test_url_check_fail(client, connect_to_db, monkeypatch):
    def make_request_fail(url):
        return None

    monkeypatch.setattr(requests, 'get', make_request_fail)

    response = client.post('/urls/10/checks', data={})

    with client.session_transaction() as session:
        flash_message = dict(session['_flashes']).get('error')

    assert response.status_code == 302
    assert flash_message == 'Произошла ошибка при проверке'


def test_url_check_success(client, connect_to_db, monkeypatch):
    def fake_make_request(url):
        class Response:
            status_code = 302
            headers = {'Content-Type': 'some header'}
        return Response()

    def fake_add_data_to_url_checks(cursor, params):
        pass

    monkeypatch.setattr(
        db,
        'add_data_to_url_checks',
        fake_add_data_to_url_checks,
    )
    monkeypatch.setattr(requests, 'get', fake_make_request)

    response = client.post('/urls/10/checks', data={})

    with client.session_transaction() as session:
        flash_message = dict(session['_flashes']).get('success')

    assert response.status_code == 302
    assert flash_message == 'Страница успешно проверена'
