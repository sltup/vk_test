#!/bin/bash
set -e

# Загружаем переменные из .env
export $(grep -v '^#' /app/.env | xargs)

echo "▶️  Запуск transform.py..."
python /app/transform.py >> /var/log/transform.log 2>&1