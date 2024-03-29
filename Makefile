install:
	poetry install

build:
	./build.sh

lint:
	poetry run flake8 page_analyzer

test:
	poetry run pytest tests

test-coverage:
	poetry run pytest --cov=page_analyzer --cov-report xml

selfcheck:
	poetry check

check: selfcheck test lint

isort:
	poetry run isort page_analyzer

dev:
	poetry run flask --app page_analyzer:app run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

.PHONY: install lint selfcheck check isort dev start