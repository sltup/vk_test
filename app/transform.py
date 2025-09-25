import os
import psycopg2
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def transform():
    pg_host = os.getenv("PGHOST")
    pg_port = os.getenv("PGPORT")
    pg_user = os.getenv("POSTGRES_USER")
    pg_password = os.getenv("POSTGRES_PASSWORD")
    pg_db = os.getenv("POSTGRES_DB")

    if not all([pg_host, pg_port, pg_user, pg_password, pg_db]):
        logging.error("❌ Нет параметров подключения к БД (PG* env)")
        return

    try:
        conn = psycopg2.connect(
            host=pg_host,
            port=pg_port,
            user=pg_user,
            password=pg_password,
            dbname=pg_db,
        )
        cur = conn.cursor()

        # Создаём схему для аналитики
        cur.execute("CREATE SCHEMA IF NOT EXISTS cdm;")

        # Создаём итоговую таблицу
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cdm.top_users_by_posts (
                user_id INT PRIMARY KEY,
                post_count INT NOT NULL,
                calculated_at TIMESTAMP
            );
        """)

        # Чистим таблицу перед загрузкой
        cur.execute("TRUNCATE cdm.top_users_by_posts;")

        # Агрегируем данные
        cur.execute("""
            INSERT INTO cdm.top_users_by_posts (user_id, post_count, calculated_at)
            SELECT user_id, COUNT(*) as post_count, current_timestamp as calculated_at
            FROM raw_.users_by_posts
            GROUP BY user_id
            ORDER BY post_count DESC;
        """)

        conn.commit()
        cur.close()
        conn.close()
        logging.info("✅ Трансформация завершена, данные переложены в cdm.top_users_by_posts")

    except Exception as e:
        logging.error(f"Ошибка трансформации: {e}")


if __name__ == "__main__":
    transform()
