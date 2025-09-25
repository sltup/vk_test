import pytest
import requests
from extract import fetch_data, save_to_postgres
import psycopg2


def test_fetch_data_success(requests_mock):
    """Проверка, что функция возвращает данные при корректном ответе API"""
    url = "https://jsonplaceholder.typicode.com/posts"
    mock_response = [{"id": 1, "title": "test", "body": "hello"}]

    requests_mock.get(url, json=mock_response, status_code=200)

    data = fetch_data()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["title"] == "test"


def test_fetch_data_error(requests_mock):
    """Проверка, что при ошибке HTTP функция выбрасывает исключение"""
    url = "https://jsonplaceholder.typicode.com/posts"
    requests_mock.get(url, status_code=500)

    with pytest.raises(requests.exceptions.HTTPError):
        fetch_data()


def test_save_to_db_inserts_data(postgresql):
    """Проверка, что данные сохраняются в PostgreSQL"""
    # Создаём соединение с тестовой БД
    conn = psycopg2.connect(**postgresql.dsn())
    cur = conn.cursor()

    # Создаём схему и таблицу
    cur.execute("""
        CREATE SCHEMA IF NOT EXISTS raw_;
        CREATE TABLE raw_.posts (
            id SERIAL PRIMARY KEY,
            title TEXT,
            body TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()

    # Подготавливаем данные для вставки
    data = [{"title": "pytest title", "body": "pytest body"}]

    # Подменяем параметры подключения
    postgresql_params = postgresql.dsn()
    save_to_postgres.__defaults__ = (
        postgresql_params["host"],
        postgresql_params["port"],
        postgresql_params["user"],
        postgresql_params["password"],
        postgresql_params["dbname"],
    )

    # Сохраняем данные
    save_to_postgres(data)

    # Проверяем, что запись добавилась
    cur.execute("SELECT title, body FROM raw_.posts;")
    rows = cur.fetchall()

    assert len(rows) == 1
    assert rows[0][0] == "pytest title"
    assert rows[0][1] == "pytest body"

    cur.close()
    conn.close()
