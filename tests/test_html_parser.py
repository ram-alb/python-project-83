from pathlib import Path

import pytest
from page_analyzer.html_parser import parse_html

FIXT_PATH = Path('tests/fixtures/html_parser')

full_result = {
    'title': 'Test Title',
    'description': 'Test Description',
    'h1': 'Test Heading',
}

no_title_result = full_result.copy()
no_title_result['title'] = None

no_description_result = full_result.copy()
no_description_result['description'] = None

no_h1_result = full_result.copy()
no_h1_result['h1'] = None


def read_file(file_path):
    with open(file_path, 'r') as file_obj:
        return file_obj.read()


@pytest.mark.parametrize(
    'html_path,expected',
    [
        (FIXT_PATH / 'full.html', full_result),
        (FIXT_PATH / 'no_description.html', no_description_result),
        (FIXT_PATH / 'no_h1.html', no_h1_result),
        (FIXT_PATH / 'no_title.html', no_title_result),
    ]
)
def test_parse_html(html_path, expected):
    html = read_file(html_path)

    assert parse_html(html) == expected
