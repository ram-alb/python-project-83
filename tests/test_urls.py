import psycopg2
from page_analyzer import sql


def test_urls_list(client, monkeypatch):
    def fake_get_from_urls(data_type):
        return [
            (1, 'http://example.com'),
            (2, 'http://test.com'),
        ]

    monkeypatch.setattr(sql, 'get_from_urls', fake_get_from_urls)

    response = client.get('/urls')

    assert response.status_code == 200
    assert 'http://example.com' in response.text
    assert 'http://test.com' in response.text


def test_invalid_url_add(client):
    response = client.post('/urls', data={
        'url': 'invalid_url',
    })

    assert 'Некорректный URL' in response.text


def test_existing_url_add(client, monkeypatch):
    def fake_add_data_to_db(table, params):
        raise psycopg2.errors.UniqueViolation

    def fake_get_from_urls(data_type, params):
        return 55

    monkeypatch.setattr(sql, 'add_data_to_db', fake_add_data_to_db)
    monkeypatch.setattr(sql, 'get_from_urls', fake_get_from_urls)

    response = client.post('/urls', data={
        'url': 'http://someurl.com',
    })

    with client.session_transaction() as session:
        flash_message = dict(session['_flashes']).get('error')

    assert response.status_code == 302
    assert flash_message == 'Страница уже существует'
    assert '<a href="/urls/55">/urls/55</a>' in response.text


def test_success_url_add(client, monkeypatch):
    def fake_add_data_to_db(table, params):
        pass

    def fake_get_from_urls(data_type, params):
        return 55

    monkeypatch.setattr(sql, 'add_data_to_db', fake_add_data_to_db)
    monkeypatch.setattr(sql, 'get_from_urls', fake_get_from_urls)

    response = client.post('/urls', data={
        'url': 'https://someurl.com',
    })

    with client.session_transaction() as session:
        flash_message = dict(session['_flashes']).get('success')

    assert response.status_code == 302
    assert '<a href="/urls/55">/urls/55</a>' in response.text
    assert flash_message == 'Страница успешно добавлена'
