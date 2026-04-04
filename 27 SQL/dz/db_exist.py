import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def make_sure_db_exists(db_name, pg_user, pg_password):
    conn = None
    exists = False
    try:
        # Подключаемся к системной базе данных
        conn = psycopg2.connect(
            # dbname=db_name,
            user=pg_user,
            password=pg_password,
            host='localhost',
            port='5432'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Запрос к системному каталогу
        cur.execute("SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname = %s)", (db_name,))
        exists = cur.fetchone()[0]
        if not exists:
            query = sql.SQL("create database {}").format(sql.Identifier(db_name))
            cur.execute(query)

        cur.close()
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if conn:
            conn.close()
    return exists
