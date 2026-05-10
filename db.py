from contextlib import contextmanager

import mysql.connector
from flask import current_app


def get_connection(database=True):
    cfg = current_app.config
    kwargs = {
        "host": cfg["DB_HOST"],
        "port": cfg["DB_PORT"],
        "user": cfg["DB_USER"],
        "password": cfg["DB_PASSWORD"],
        "connection_timeout": cfg["DB_CONNECTION_TIMEOUT"],
    }
    if database:
        kwargs["database"] = cfg["DB_NAME"]
    return mysql.connector.connect(**kwargs)


@contextmanager
def db_cursor(dictionary=True, commit=False):
    conn = get_connection()
    cursor = conn.cursor(dictionary=dictionary)
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
