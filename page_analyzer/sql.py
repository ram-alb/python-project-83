import os

import psycopg2


def execute_sql(sql_type, sql_command, sql_params):
    with psycopg2.connect(os.getenv('DATABASE_URL')) as conn:
        with conn.cursor() as cur:
            cur.execute(sql_command, sql_params)
            if sql_type == 'select':
                return cur.fetchall()


def get_from_urls(data_type, params={}):
    get_url_id = """
        SELECT id
        FROM urls
        WHERE name = %(name)s;
    """

    get_url_data = """
        SELECT id, name, created_at
        FROM urls
        WHERE id = %(id)s;
    """

    get_all_urls = """
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

    sql_selects = {
        'get_url_id': get_url_id,
        'get_url_data': get_url_data,
        'get_all_urls': get_all_urls,
    }

    selected_data = execute_sql('select', sql_selects[data_type], params)
    if data_type == 'get_url_id':
        return selected_data[0][0]
    elif data_type == 'get_url_data':
        return selected_data[0]
    return selected_data


def get_from_url_checks(url_id):
    select_by_url_id = """
        SELECT * FROM url_checks
        WHERE url_id = %(url_id)s
        ORDER BY id DESC;
    """

    return execute_sql('select', select_by_url_id, {'url_id': url_id})


def add_data_to_db(table, params):
    insert_url = """
        INSERT INTO urls (name, created_at)
        VALUES (%(name)s, %(created_at)s);
    """

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

    inserts = {
        'urls': insert_url,
        'url_checks': insert_url_check,
    }
    execute_sql('insert', inserts[table], params)
