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

UrlItem = namedtuple(
    'UrlItem',
    ['id', 'name', 'status_code', 'last_check'],
)

expected_urls = [
    UrlItem(2, 'https://url2.com', 200, '2024-01-15'),
    UrlItem(1, 'https://url1.com', 200, '2024-01-13'),
]

expected_urls_checks_empty = [
    UrlItem(2, 'https://url2.com', None, None),
    UrlItem(1, 'https://url1.com', None, None),
]

expected_urls_db_empty = []


def fake_fetch_all_urls(cursor, sql_command, sql_params=None):
    SelectUrlChecks = namedtuple(
        'SelectUrlChecks',
        ['url_id', 'status_code', 'created_at'],
    )
    selected_url_checks = [
        SelectUrlChecks(url_id=2, status_code=200, created_at='2024-01-15'),
        SelectUrlChecks(url_id=1, status_code=200, created_at='2024-01-13'),
    ]

    if 'url_checks' in sql_command:
        return selected_url_checks

    return selected_urls


def fake_fetch_all_url_checks_empty(cursor, sql_command, sql_params=None):
    selected_url_checks = []
    if 'url_checks' in sql_command:
        return selected_url_checks

    return selected_urls


def fake_fetch_all_db_empty(cursor, sql_command, sql_params=None):
    return []


@pytest.mark.parametrize(
    'fake_fetch_all,expected',
    [
        (fake_fetch_all_urls, expected_urls),
        (fake_fetch_all_url_checks_empty, expected_urls_checks_empty),
        (fake_fetch_all_db_empty, expected_urls_db_empty),
    ]
)
def test_get_all_url(monkeypatch, fake_fetch_all, expected):
    monkeypatch.setattr(db, 'fetch_all', fake_fetch_all)

    assert db.get_all_urls('cursor') == expected
