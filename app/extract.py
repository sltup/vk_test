from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import psycopg2
import os
import sys
import time
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

TABLE_NAME = "raw_.users_by_posts"

# === Настройка логов ===
load_dotenv()  # загружаем .env для LOG_FILE и LOGLEVEL
LOG_FILE = os.getenv("LOG_FILE", "/var/log/myscript.log")
LOG_LEVEL = os.getenv("LOGLEVEL", "INFO").upper()

log_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
)
log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
log_handler.setFormatter(log_formatter)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    handlers=[logging.StreamHandler(sys.stdout), log_handler]
)


# === API с retry ===
def get_session_with_retries():
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def fetch_data(api_url):
    logging.info(f"Запрос к API: {api_url}")
    session = get_session_with_retries()
    try:
        response = session.get(api_url, timeout=30)
        response.raise_for_status()
        logging.info("Успешно получили данные из API")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при запросе к API после всех попыток: {e}")
        raise


# === PostgreSQL с retry ===
def connect_with_retries(db_config, retries=5, delay=5):
    for attempt in range(1, retries + 1):
        try:
            conn = psycopg2.connect(**db_config)
            logging.info("Подключение к PostgreSQL успешно")
            return conn
        except psycopg2.OperationalError as e:
            logging.warning(f"Попытка {attempt}/{retries}: не удалось подключиться к БД: {e}")
            if attempt < retries:
                time.sleep(delay * attempt)  # экспоненциальная пауза
            else:
                logging.error("Все попытки подключения к PostgreSQL исчерпаны")
                raise


def save_to_postgres(data, db_config):
    try:
        conn = connect_with_retries(db_config)
        cur = conn.cursor()

        create_table_sql = f"""
            CREATE SCHEMA IF NOT EXISTS raw_;
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id SERIAL PRIMARY KEY,
                user_id INT,
                title TEXT,
                body TEXT,
                created_dttm TIMESTAMP
            );
        """
        logging.debug(f"SQL: {create_table_sql.strip()}")
        cur.execute(create_table_sql)

        insert_sql = f"""
            INSERT INTO {TABLE_NAME} (id, user_id, title, body, created_dttm)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """
        for item in data:
            params = [item["id"], item["userId"], item["title"], item["body"], datetime.today().strftime('%Y-%m-%d %H:%M:%S')]
            logging.debug(f"SQL: {insert_sql.strip()} | params={params}")
            cur.execute(insert_sql, params)

        conn.commit()
        cur.close()
        conn.close()
        logging.info(f"Сохранено {len(data)} записей в таблицу {TABLE_NAME}")

    except Exception as e:
        logging.error(f"Ошибка при работе с PostgreSQL: {e}")
        raise


# === Конфигурация через аргументы или .env ===
def get_config():
    # parser = argparse.ArgumentParser(description="Парсинг JSON API и сохранение в PostgreSQL")
    # parser.add_argument("--host", help="Хост PostgreSQL")
    # parser.add_argument("--port", type=int, help="Порт PostgreSQL")
    # parser.add_argument("--database", help="Имя базы данных")
    # parser.add_argument("--user", help="Пользователь PostgreSQL")
    # parser.add_argument("--password", help="Пароль PostgreSQL")
    # parser.add_argument("--api", help="URL API для получения JSON")
    # args = parser.parse_args()
    #
    # db_config = {
    #     "host": args.host or os.getenv("PGHOST"),
    #     "port": args.port or int(os.getenv("PGPORT", 5432)),
    #     "database": args.database or os.getenv("PGDATABASE"),
    #     "user": args.user or os.getenv("PGUSER"),
    #     "password": args.password or os.getenv("PGPASSWORD"),
    # }
    #
    # api_url = args.api or os.getenv("API_URL")

    db_config = {
        "host": os.getenv("PGHOST", "db"),
        "port": int(os.getenv("PGPORT", 5432)),
        "database": os.getenv("POSTGRES_DB"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD")
    }
    api_url = os.getenv("API_URL")

    if not all(db_config.values()) or not api_url:
        logging.error("Ошибка: не хватает параметров подключения или API_URL")
        logging.error("".join([str(i) for i in db_config.values()]), api_url)
        sys.exit(1)

    return db_config, api_url


# === Main ===
if __name__ == "__main__":
    logging.info("=== Запуск скрипта ===")
    db_config, api_url = get_config()
    json_data = fetch_data(api_url)
    save_to_postgres(json_data, db_config)
    logging.info("=== Скрипт завершён ===")
