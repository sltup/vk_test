1) Поднять Docker
2) Дать права на исполнение скрипта - chmod +x run.sh
3) Запустить ./run.sh (или через docker compose up --build)
4) Срез данных - docker compose exec db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT * FROM cdm.top_users_by_posts LIMIT 20;"

