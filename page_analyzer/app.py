import os
from datetime import date
from urllib.parse import urlparse

import psycopg2
import validators
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from . import sql

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
    all_urls = sql.get_data_from_db('get_all_urls')
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
        sql.add_data_to_db(insert_params)
    except psycopg2.errors.UniqueViolation:
        flash('Страница уже существует', 'error')
    else:
        flash('Страница успешно добавлена', 'success')

    url_id = sql.get_data_from_db('get_url_id', {'name': name})
    return redirect(url_for('url_details', id=url_id))


@app.route('/urls/<id>')
def url_details(id):
    url_id, name, created_at = sql.get_data_from_db('get_url_data', {'id': id})
    return render_template(
        'url_details.html',
        id=url_id, name=name,
        created_at=created_at,
    )
