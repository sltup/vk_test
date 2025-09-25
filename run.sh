#!/bin/bash
set -e

echo "🚀 Билдим и запускаем docker-compose..."
docker compose up -d --build

echo "⏳ Ждём, пока сервисы станут healthy..."
docker compose ps

# Запустим extract → transform вручную (для проверки без cron)
echo "▶️  Extract..."
docker compose run --rm app python /app/extract.py

echo "▶️  Transform..."
docker compose run --rm app python /app/transform.py

echo "Пайплайн отработал! Логи cron можно смотреть так:"
echo "   docker compose logs -f app"
