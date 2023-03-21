"""Fixtures for tests."""
import pytest
from page_analyzer import app


@pytest.fixture()
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client
