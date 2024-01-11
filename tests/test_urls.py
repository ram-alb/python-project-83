import psycopg2
from page_analyzer import db


def test_urls_list(client, monkeypatch):
    def fake_get_all_urls():
        return [
            {'id': 1, 'name': 'http://example.com'},
            {'id': 2, 'name': 'http://test.com'},
        ]

    monkeypatch.setattr(db, 'get_all_urls', fake_get_all_urls)

    response = client.get('/urls')

    assert response.status_code == 200
    assert 'http://example.com' in response.text
    assert 'http://test.com' in response.text


def test_invalid_url_add(client):
    response = client.post('/urls', data={
        'url': 'invalid_url',
    })

    assert 'Некорректный URL' in response.text
    assert response.status_code == 422


def test_existing_url_add(client, monkeypatch):
    def fake_add_data_to_urls(params):
        raise psycopg2.errors.UniqueViolation

    def fake_get_url_id(url_name):
        return 55

    monkeypatch.setattr(db, 'add_data_to_urls', fake_add_data_to_urls)
    monkeypatch.setattr(db, 'get_url_id', fake_get_url_id)

    response = client.post('/urls', data={
        'url': 'http://someurl.com',
    })

    with client.session_transaction() as session:
        flash_message = dict(session['_flashes']).get('error')

    assert response.status_code == 302
    assert flash_message == 'Страница уже существует'
    assert '<a href="/urls/55">/urls/55</a>' in response.text


def test_success_url_add(client, monkeypatch):
    def fake_add_data_to_urls(params):
        pass

    def fake_get_url_id(url_name):
        return 55

    monkeypatch.setattr(db, 'add_data_to_urls', fake_add_data_to_urls)
    monkeypatch.setattr(db, 'get_url_id', fake_get_url_id)

    response = client.post('/urls', data={
        'url': 'https://someurl.com',
    })

    with client.session_transaction() as session:
        flash_message = dict(session['_flashes']).get('success')

    assert response.status_code == 302
    assert '<a href="/urls/55">/urls/55</a>' in response.text
    assert flash_message == 'Страница успешно добавлена'
