#!/bin/bash
set -e

export $(grep -v '^#' .env | xargs)

docker compose up -d --build
docker compose ps

# Запустим extract → transform вручную (для проверки без cron)
echo "extract..."
docker compose run --rm app python /app/extract.py

echo "transform..."
docker compose run --rm app python /app/transform.py

echo "Сырые данные. Топ 20"
docker compose exec -T db bash -c "PGPASSWORD='$POSTGRES_PASSWORD' psql -U '$POSTGRES_USER' -d '$POSTGRES_DB' -P pager=off -P border=2 -P format=aligned -c \"SELECT * FROM raw_.users_by_posts LIMIT 20;\""

echo "Предобработанные данные. Топ 10"
docker compose exec -T db bash -c "PGPASSWORD='$POSTGRES_PASSWORD' psql -U '$POSTGRES_USER' -d '$POSTGRES_DB' -P pager=off -P border=2 -P format=aligned -c \"SELECT * FROM cdm.top_users_by_posts LIMIT 30;\""

echo "Пайплайн отработал! Логи cron можно смотреть так:"
echo "   docker compose logs -f app"
