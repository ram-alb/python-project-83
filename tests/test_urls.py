import psycopg2
from page_analyzer import db


def test_get_urls_list(client, connect_to_db):
    response = client.get('/urls')

    assert response.status_code == 200
    assert '<h1>Сайты</h1>' in response.text
    assert 'http://example.com' in response.text
    assert 'http://test.com' in response.text


def test_post_urls_empty_url(client):
    response = client.post('/urls', data={
        'url': '',
    })

    assert response.status_code == 422
    assert 'URL обязателен' in response.text


def test_post_urls_long_url(client):
    very_long_url = ''.join('a' for _ in range(256))
    response = client.post('/urls', data={
        'url': very_long_url,
    })

    assert response.status_code == 422
    assert 'URL превышает 255 символов' in response.text


def test_post_urls_invalid_url(client):
    response = client.post('/urls', data={
        'url': 'invalid_url',
    })

    assert response.status_code == 422
    assert 'Некорректный URL' in response.text


def test_post_urls_existing_url(client, connect_to_db, monkeypatch):
    def fake_add_data_to_urls(cursor, params):
        raise psycopg2.errors.UniqueViolation

    monkeypatch.setattr(db, 'add_data_to_urls', fake_add_data_to_urls)

    response = client.post('/urls', data={
        'url': 'http://someurl.com',
    })

    with client.session_transaction() as session:
        flash_message = dict(session['_flashes']).get('error')

    assert response.status_code == 302
    assert flash_message == 'Страница уже существует'
    assert '<a href="/urls/55">/urls/55</a>' in response.text


def test_post_urls_success(client, connect_to_db, monkeypatch):
    def fake_add_data_to_urls(cursor, params):
        pass

    monkeypatch.setattr(db, 'add_data_to_urls', fake_add_data_to_urls)

    response = client.post('/urls', data={
        'url': 'https://someurl.com',
    })

    with client.session_transaction() as session:
        flash_message = dict(session['_flashes']).get('success')

    assert response.status_code == 302
    assert '<a href="/urls/55">/urls/55</a>' in response.text
    assert flash_message == 'Страница успешно добавлена'
