from collections import namedtuple

import psycopg2
from psycopg2.extras import NamedTupleCursor


def connect_to_db(app):
    return psycopg2.connect(
        app.config['DATABASE_URL'],
        cursor_factory=NamedTupleCursor,
    )


def commit_db(connection):
    return connection.commit()


def rollback_db(connection):
    return connection.rollback()


def close_db(connection):
    return connection.close()


def get_all_urls(connection):
    select_urls = """
        SELECT id, name
        FROM urls
        ORDER BY id DESC;
    """

    select_url_checks = """
        SELECT
            DISTINCT ON (url_id) url_id,
            status_code,
            created_at
        FROM url_checks
        ORDER BY
            url_id,
            id DESC;
    """
    with connection.cursor() as cursor:
        cursor.execute(select_urls)
        selected_urls = cursor.fetchall()
        cursor.execute(select_url_checks)
        selected_url_checks = cursor.fetchall()

    url_checks_dict = {
        check.url_id: check for check in selected_url_checks
    }

    urls = []
    url_item = namedtuple(
        'UrlItem',
        ['id', 'name', 'status_code', 'last_check'],
    )
    for selected_url in selected_urls:
        check = url_checks_dict.get(selected_url.id, None)
        url = url_item(
            id=selected_url.id,
            name=selected_url.name,
            status_code=check.status_code if check else None,
            last_check=check.created_at if check else None,
        )
        urls.append(url)
    return urls


def get_url_id(connection, url_name):
    sql_select = """
        SELECT id
        FROM urls
        WHERE name = %(name)s;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql_select, {'name': url_name})
        selected_url_id = cursor.fetchone()
    return selected_url_id.id


def get_url_data(connection, url_id):
    sql_select = """
        SELECT id, name, created_at
        FROM urls
        WHERE id = %(id)s;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql_select, {'id': url_id})
        return cursor.fetchone()


def get_from_url_checks(connection, url_id):
    select_by_url_id = """
        SELECT * FROM url_checks
        WHERE url_id = %(url_id)s
        ORDER BY id DESC;
    """
    with connection.cursor() as cursor:
        cursor.execute(select_by_url_id, {'url_id': url_id})
        return cursor.fetchall()


def add_data_to_urls(connection, params):
    insert_url = """
        INSERT INTO urls (name, created_at)
        VALUES (%(name)s, %(created_at)s);
    """
    with connection.cursor() as cursor:
        cursor.execute(insert_url, params)


def add_data_to_url_checks(connection, params):
    insert_url_check = """
        INSERT INTO url_checks (
            url_id,
            status_code,
            h1,
            title,
            description,
            created_at
        )
        VALUES (
            %(url_id)s,
            %(status_code)s,
            %(h1)s,
            %(title)s,
            %(description)s,
            %(created_at)s);
    """

    with connection.cursor() as cursor:
        cursor.execute(insert_url_check, params)
