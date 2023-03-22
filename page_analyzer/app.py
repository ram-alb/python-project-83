import os
from datetime import date
from urllib.parse import urlparse

import psycopg2
import validators
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from . import sql
from .html_parser import parse_html
from .http_requests import make_request

load_dotenv()

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    url = ''
    error = ''
    return render_template('index.html', url=url, error=error)


@app.get('/urls')
def urls_list():
    all_urls = sql.get_from_urls('get_all_urls')
    return render_template('urls.html', urls=all_urls)


@app.post('/urls')
def url_add():
    url = request.form.get('url')
    if not validators.url(url):
        flash('Некорректный URL', 'error')
        return render_template('index.html', url=url)

    parsed_url = urlparse(url)
    name = f'{parsed_url.scheme}://{parsed_url.netloc}'

    insert_params = {
        'name': name,
        'created_at': date.today(),
    }
    try:
        sql.add_data_to_db('urls', insert_params)
    except psycopg2.errors.UniqueViolation:
        flash('Страница уже существует', 'error')
    else:
        flash('Страница успешно добавлена', 'success')

    url_id = sql.get_from_urls('get_url_id', {'name': name})
    return redirect(url_for('url_details', id=url_id))


@app.route('/urls/<id>')
def url_details(id):
    url_data = sql.get_from_urls('get_url_data', {'id': id})
    url_checks = sql.get_from_url_checks(url_data[0])
    return render_template(
        'url_details.html',
        url_data=url_data,
        url_checks=url_checks,
    )


@app.post('/urls/<id>/checks')
def url_check(id):
    url_data = sql.get_from_urls('get_url_data', {'id': id})

    response = make_request(url_data[1])
    if not response:
        flash('Произошла ошибка при проверке', 'error')
        return redirect(url_for('url_details', id=id))

    if 'html' in response.headers['Content-Type']:
        html_data = parse_html(response.text)
    else:
        html_data = {
            'h1': None,
            'title': None,
            'description': None,
        }

    sql.add_data_to_db('url_checks', {
        'url_id': id,
        'status_code': response.status_code,
        'created_at': date.today(),
        **html_data
    })

    flash('Страница успешно проверена', 'success')

    return redirect(url_for('url_details', id=id))
