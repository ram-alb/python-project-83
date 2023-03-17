import os

import psycopg2


def execute_sql(sql_type, sql_command, sql_params):
    with psycopg2.connect(os.getenv('DATABASE_URL')) as conn:
        with conn.cursor() as cur:
            cur.execute(sql_command, sql_params)
            if sql_type == 'select':
                return cur.fetchall()


def get_data_from_db(data_type, params={}):
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
        SELECT id, name
        FROM urls
        ORDER BY id DESC;
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


def add_data_to_db(params):
    insert_url = """
        INSERT INTO urls (name, created_at)
        VALUES (%(name)s, %(created_at)s);
    """
    execute_sql('insert', insert_url, params)