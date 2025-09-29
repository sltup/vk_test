1) Склоинровать репозиторий
2) Создать .env file в корне проекта со следующими атрибутами:
   - PGHOST=your_postgres_host
   - PGPORT=your_postgres_port
   - POSTGRES_DB=your_postgres_database_name
   - POSTGRES_USER=your_postgres_user
   - POSTGRES_PASSWORD=your_passport
   - API_URL=https://jsonplaceholder.typicode.com/posts
   - LOG_FILE=/var/log/myscript.log (путь к скрипту на развернутой машинке)
   - LOGLEVEL=INFO (уровень логирования)
2) Поднять Docker
2) Дать права на исполнение скрипта - sudo chmod +x run.sh
3) Запустить ./run.sh (или через docker compose up --build)
4) Срез данных - docker compose exec db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT * FROM cdm.top_users_by_posts LIMIT 100;"

