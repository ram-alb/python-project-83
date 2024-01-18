import os
from datetime import date
from urllib.parse import urlparse

import psycopg2
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from . import db
from .html_parser import parse_html
from .http_requests import make_request
from .validation import validate_url

load_dotenv()

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def urls_list():
    connection_to_db = db.connect_to_db(app)
    with connection_to_db.cursor() as cursor:
        all_urls = db.get_all_urls(cursor)
    connection_to_db.close()
    return render_template('urls.html', urls=all_urls)


@app.post('/urls')
def url_add():
    url = request.form.get('url')
    is_valid_url, url_error = validate_url(url)
    if not is_valid_url:
        flash(url_error, 'error')
        return render_template('index.html', url=url), 422

    parsed_url = urlparse(url)
    url_name = f'{parsed_url.scheme}://{parsed_url.netloc}'

    insert_params = {
        'name': url_name,
        'created_at': date.today(),
    }

    connection_to_db = db.connect_to_db(app)
    with connection_to_db.cursor() as cursor:
        try:
            db.add_data_to_urls(cursor, insert_params)
        except psycopg2.errors.UniqueViolation:
            flash('Страница уже существует', 'error')
            connection_to_db.rollback()
        else:
            flash('Страница успешно добавлена', 'success')
            connection_to_db.commit()

        url_id = db.get_url_id(cursor, url_name)
    connection_to_db.close()

    return redirect(url_for('url_details', id=url_id))


@app.route('/urls/<int:id>')
def url_details(id):
    connection_to_db = db.connect_to_db(app)
    with connection_to_db.cursor() as cursor:
        url_data = db.get_url_data(cursor, id)
        url_checks = db.get_from_url_checks(cursor, id)
    connection_to_db.close()

    return render_template(
        'url_details.html',
        url_data=url_data,
        url_checks=url_checks,
    )


@app.post('/urls/<int:id>/checks')
def url_check(id):
    connection_to_db = db.connect_to_db(app)

    with connection_to_db.cursor() as cursor:
        url_data = db.get_url_data(cursor, id)

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

        db.add_data_to_url_checks(
            cursor,
            {
                'url_id': id,
                'status_code': response.status_code,
                'created_at': date.today(),
                **html_data
            },
        )
        connection_to_db.commit()
        flash('Страница успешно проверена', 'success')

    connection_to_db.close()

    return redirect(url_for('url_details', id=id))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500
