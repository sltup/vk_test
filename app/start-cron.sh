#!/bin/bash
set -e
export $(grep -v '^#' /app/.env | xargs)

echo "🚀 Старт пайплайна (extract -> transform) в бесконечном цикле"

while true; do
    echo "▶️  Запуск extract.py..."
    python /app/extract.py >> /var/log/extract.log 2>&1 || echo "❌ Ошибка extract"

    echo "⏱ Ждём ${SLEEP_INTERVAL_EXTRACT:-60} секунд перед transform..."
    sleep ${SLEEP_INTERVAL_EXTRACT:-60}

    echo "▶️  Запуск transform.py..."
    python /app/transform.py >> /var/log/transform.log 2>&1 || echo "❌ Ошибка transform"

    echo "⏱ Ждём ${SLEEP_INTERVAL_TRANSFORM:-60} секунд до следующего цикла..."
    sleep ${SLEEP_INTERVAL_TRANSFORM:-60}
done