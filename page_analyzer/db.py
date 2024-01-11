import psycopg2
from flask import current_app
from psycopg2.extras import NamedTupleCursor


def connect_to_db():
    return psycopg2.connect(
        current_app.config['DATABASE_URL'],
        cursor_factory=NamedTupleCursor,
    )


def fetch_all(sql_command, sql_params=None):
    connection = connect_to_db()
    with connection.cursor() as cur:
        cur.execute(sql_command, sql_params)
        selected_data = cur.fetchall()
    connection.close()
    return selected_data


def fetch_one(sql_command, sql_params=None):
    connection = connect_to_db()
    with connection.cursor() as cur:
        cur.execute(sql_command, sql_params)
        selected_data = cur.fetchone()
    connection.close()
    return selected_data


def insert_to_db(sql_command, sql_params=None):
    connection = connect_to_db()
    with connection.cursor() as cur:
        cur.execute(sql_command, sql_params)
    connection.commit()
    connection.close()


def get_all_urls():
    sql_select = """
        SELECT urls.id, urls.name, checks.last_check, checks.status_code
        FROM urls
        LEFT JOIN (
            SELECT
                DISTINCT ON (url_id) url_id,
                status_code,
                created_at as last_check
            FROM url_checks
            ORDER BY
                url_id,
                id DESC
        ) checks
            ON (urls.id = checks.url_id)
        ORDER BY urls.id DESC;
    """

    return fetch_all(sql_select)


def get_url_id(url_name):
    sql_select = """
        SELECT id
        FROM urls
        WHERE name = %(name)s;
    """
    selected_url_id = fetch_one(sql_select, {'name': url_name})
    return selected_url_id.id


def get_url_data(url_id):
    sql_select = """
        SELECT id, name, created_at
        FROM urls
        WHERE id = %(id)s;
    """
    return fetch_one(sql_select, {'id': url_id})


def get_from_url_checks(url_id):
    select_by_url_id = """
        SELECT * FROM url_checks
        WHERE url_id = %(url_id)s
        ORDER BY id DESC;
    """

    return fetch_all(select_by_url_id, {'url_id': url_id})


def add_data_to_urls(params):
    insert_url = """
        INSERT INTO urls (name, created_at)
        VALUES (%(name)s, %(created_at)s);
    """
    insert_to_db(insert_url, params)


def add_data_to_url_checks(params):
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

    insert_to_db(insert_url_check, params)
