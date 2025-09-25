
FROM python:3.12-slim

RUN apt-get update && apt-get install -y cron gcc libpq-dev dos2unix && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY extract.py transform.py requirements.txt crontab.txt start-cron.sh ./

RUN dos2unix start-cron.sh && \
    chmod +x start-cron.sh

RUN pip install --no-cache-dir -r requirements.txt

# Создаём папку для логов
RUN mkdir -p /var/log && touch /var/log/myscript.log

# Устанавливаем crontab
COPY crontab.txt /etc/cron.d/my-cron
RUN chmod 0644 /etc/cron.d/my-cron
RUN crontab /etc/cron.d/my-cron
RUN chmod +x /etc/cron.d/my-cron


# # CMD запускает shell-скрипт
CMD ["./start-cron.sh"]
