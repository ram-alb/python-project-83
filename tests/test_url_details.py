def test_url_details(client, connect_to_db):
    response = client.get('/urls/10')

    assert response.status_code == 200
    assert '<td>10</td>' in response.text
    assert '<td>http://someurl.com</td>' in response.text
    assert '<td>1</td>' in response.text
    assert '<td>2023-02-20</td>' in response.text
