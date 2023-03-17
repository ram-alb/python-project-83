import psycopg2
from page_analyzer import sql


def test_urls_list(client):
    def fake_get_data_from_db(data_type):
        return [
            (1, 'https://url1.com'),
            (2, 'https://url2.com'),
        ]
    sql.get_data_from_db = fake_get_data_from_db

    response = client.get('/urls')

    assert response.status_code == 200
    assert '<h1>Сайты</h1>' in response.text
    assert '<td>1</td>' in response.text
    assert '<a href="/urls/2">https://url2.com</a>' in response.text


def test_url_add_success(client):
    def fake_add_data_to_db(params):
        pass

    def fake_get_data_from_db(data_type, params):
        return 55

    sql.add_data_to_db = fake_add_data_to_db
    sql.get_data_from_db = fake_get_data_from_db

    response = client.post('/urls', data={
        'url': 'https://url55.com',
    })

    with client.session_transaction() as session:
        flash_message = dict(session['_flashes']).get('success')

    assert response.status_code == 302
    assert '<a href="/urls/55">/urls/55</a>' in response.text
    assert flash_message == 'Страница успешно добавлена'


def test_url_add_fail(client):
    def fake_add_data_to_db(params):
        raise psycopg2.errors.UniqueViolation

    def fake_get_data_from_db(data_type, params):
        return 55

    sql.add_data_to_db = fake_add_data_to_db
    sql.get_data_from_db = fake_get_data_from_db

    response = client.post('/urls', data={
        'url': 'https://url55.com',
    })

    with client.session_transaction() as session:
        flash_message = dict(session['_flashes']).get('error')

    assert response.status_code == 302
    assert '<a href="/urls/55">/urls/55</a>' in response.text
    assert flash_message == 'Страница уже существует'
