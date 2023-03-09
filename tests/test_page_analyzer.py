def test_index(client):
    response = client.get('/')

    assert '<h1 class="display-3">Анализатор страниц</h1>' in response.text
    assert response.status_code == 200
