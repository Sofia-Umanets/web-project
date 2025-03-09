import os
from dotenv import load_dotenv
import mysql.connector

from request_validators import RequestModel

# Загрузка переменных окружения из файла .env
load_dotenv()

db_config = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD"),
    "database": os.environ.get("DB_NAME", "form_data"),
}

def database_connection(function):
    def inner(*args, **kwargs):
        with mysql.connector.connect(**db_config) as conn:
            return function(*args, connection=conn, **kwargs)
    return inner

@database_connection
def insert_request(request: RequestModel, **kwargs):
    conn = kwargs["connection"]

    INSERT_REQUEST_SQL = """
        INSERT INTO requests (name, phone, email, birthday, sex, biography)
        VALUES (%s, %s, %s, %s, %s, %s);
    """
    insert_request_data = (
        request.name, str(request.phone)[4:], request.email,
        request.birthday, request.sex, request.biography,
    )

    SELECT_LANGUAGES_SQL = """
        SELECT language_id FROM languages WHERE name IN (%s);
    """
    # Создаём строку с плейсхолдерами для IN
    placeholders = ', '.join(['%s'] * len(request.languages))
    SELECT_LANGUAGES_SQL = SELECT_LANGUAGES_SQL % placeholders

    INSERT_REQUEST_LANGUAGE_SQL = """
        INSERT INTO requests_languages (request_id, language_id)
        VALUES (%s, %s);
    """

    with conn.cursor() as cur:
        cur.execute(INSERT_REQUEST_SQL, insert_request_data)
        request_id = cur.lastrowid

        cur.execute(SELECT_LANGUAGES_SQL, request.languages)
        language_ids = [lang[0] for lang in cur.fetchall()]

        for language_id in language_ids:
            cur.execute(INSERT_REQUEST_LANGUAGE_SQL, (request_id, language_id))

        conn.commit()

