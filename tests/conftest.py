"""Fixtures for tests."""

import os

import psycopg2
import pytest
from page_analyzer import app

app.config.update({
    "TESTING": True,
})


@pytest.fixture()
def client():
    return app.test_client()
