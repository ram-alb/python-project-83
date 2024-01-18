from collections import namedtuple

import pytest
from page_analyzer import db

SelectUrl = namedtuple(
    'SelectUrl',
    ['id', 'name'],
)
selected_urls = [
    SelectUrl(id=2, name='https://url2.com'),
    SelectUrl(id=1, name='https://url1.com'),
]

SelectUrlChecks = namedtuple(
    'SelectUrlChecks',
    ['url_id', 'status_code', 'created_at'],
)
selected_url_checks = [
    SelectUrlChecks(url_id=2, status_code=200, created_at='2024-01-15'),
    SelectUrlChecks(url_id=1, status_code=200, created_at='2024-01-13'),
]

UrlItem = namedtuple(
    'UrlItem',
    ['id', 'name', 'status_code', 'last_check'],
)

expected_urls_empty_db = []

expected_urls_full_db = [
    UrlItem(2, 'https://url2.com', 200, '2024-01-15'),
    UrlItem(1, 'https://url1.com', 200, '2024-01-13'),
]

expected_urls_empty_url_checks = [
    UrlItem(2, 'https://url2.com', None, None),
    UrlItem(1, 'https://url1.com', None, None),
]


class FakeCursor:
    def __init__(self, db_data):
        self.db_data = db_data

    def execute(self, sql_command):
        pass

    def fetchall(self):
        if len(self.db_data) == 0:
            return []
        return self.db_data.pop()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class FakeConnection:
    def __init__(self, db_data):
        self.db_data = db_data

    def cursor(self):
        return FakeCursor(db_data=self.db_data)


@pytest.mark.parametrize(
    'connection,expected_urls',
    [
        (FakeConnection([]), expected_urls_empty_db),
        (
            FakeConnection([selected_url_checks, selected_urls]),
            expected_urls_full_db,
        ),
        (FakeConnection([[], selected_urls]), expected_urls_empty_url_checks),
    ]
)
def test_get_all_urls_empty_database(connection, expected_urls):
    all_urls = db.get_all_urls(connection)

    assert all_urls == expected_urls
