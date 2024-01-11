import os
from datetime import date
from urllib.parse import urlparse

import psycopg2
import validators
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from . import db
from .html_parser import parse_html
from .http_requests import make_request

load_dotenv()

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    url = ''
    error = ''
    return render_template('index.html', url=url, error=error)


@app.get('/urls')
def urls_list():
    all_urls = db.get_all_urls()
    return render_template('urls.html', urls=all_urls)


@app.post('/urls')
def url_add():
    url = request.form.get('url')
    if not validators.url(url):
        flash('Некорректный URL', 'error')
        return render_template('index.html', url=url), 422

    parsed_url = urlparse(url)
    url_name = f'{parsed_url.scheme}://{parsed_url.netloc}'

    insert_params = {
        'name': url_name,
        'created_at': date.today(),
    }
    try:
        db.add_data_to_urls(insert_params)
    except psycopg2.errors.UniqueViolation:
        flash('Страница уже существует', 'error')
    else:
        flash('Страница успешно добавлена', 'success')

    url_id = db.get_url_id(url_name)
    return redirect(url_for('url_details', id=url_id))


@app.route('/urls/<id>')
def url_details(id):
    url_data = db.get_url_data(id)
    url_checks = db.get_from_url_checks(id)

    return render_template(
        'url_details.html',
        url_data=url_data,
        url_checks=url_checks,
    )


@app.post('/urls/<id>/checks')
def url_check(id):
    url_data = db.get_url_data(id)

    response = make_request(url_data.name)
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

    db.add_data_to_url_checks({
        'url_id': id,
        'status_code': response.status_code,
        'created_at': date.today(),
        **html_data
    })

    flash('Страница успешно проверена', 'success')

    return redirect(url_for('url_details', id=id))
