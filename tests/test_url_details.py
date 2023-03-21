from page_analyzer import sql


def test_url_details(client, monkeypatch):
    def fake_get_from_urls(data_type, params):
        return (10, 'http://someurl.com', '2022-03-10')

    def fake_get_from_url_checks(url_id):
        return [
            (1, 10, '', '', '', '', '2022-04-05'),
            (2, 10, '', '', '', '', '2023-02-20'),
        ]

    monkeypatch.setattr(sql, 'get_from_urls', fake_get_from_urls)
    monkeypatch.setattr(sql, 'get_from_url_checks', fake_get_from_url_checks)

    response = client.get('/urls/10')

    assert response.status_code == 200
    assert '<td>10</td>' in response.text
    assert '<td>http://someurl.com</td>' in response.text
    assert '<td>1</td>' in response.text
    assert '<td>2023-02-20</td>' in response.text


def test_url_check(client, monkeypatch):
    def fake_add_data_to_db(table, params):
        pass

    monkeypatch.setattr(sql, 'add_data_to_db', fake_add_data_to_db)

    response = client.post('/urls/10/checks', data={})

    with client.session_transaction() as session:
        flash_message = dict(session['_flashes']).get('success')

    assert response.status_code == 302
    assert flash_message == 'Страница успешно проверена'
