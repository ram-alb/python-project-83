import pytest
from page_analyzer import app, db


class FakeConnection:
    def cursor(self):
        class FakeCursor:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                pass

        return FakeCursor()

    def commit(self):
        pass

    def close(self):
        pass


def fake_get_all_urls(cursor):
    return [
        {'id': 1, 'name': 'http://example.com'},
        {'id': 2, 'name': 'http://test.com'},
    ]


def fake_get_url_id(cursor, url_name):
    return 55


def fake_get_url_data(cursor, id):
    class UrlData:
        id = 10
        name = 'http://someurl.com'
        created_at = '2022-03-10'
    return UrlData


def fake_get_from_url_checks(cursor, url_id):
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


@pytest.fixture()
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def connect_to_db(monkeypatch):
    def fake_connect_to_db(app):
        return FakeConnection()

    monkeypatch.setattr(db, 'connect_to_db', fake_connect_to_db)
    monkeypatch.setattr(db, 'get_all_urls', fake_get_all_urls)
    monkeypatch.setattr(db, 'get_url_id', fake_get_url_id)
    monkeypatch.setattr(db, 'get_url_data', fake_get_url_data)
    monkeypatch.setattr(db, 'get_from_url_checks', fake_get_from_url_checks)
