create_content_schema:
	echo "Создать схему content в базе данных."
	docker compose up -d --build postgres
	docker exec -d postgres psql -Upostgres -d postgres -c "CREATE SCHEMA IF NOT EXISTS content;"


start-admin:
	echo "Запуск проекта"
	docker compose up -d --build backend_admin postgres nginx
	echo "Генерирую тестовые данные"
	docker exec -d postgres psql -Upostgres -d postgres -c "CREATE SCHEMA IF NOT EXISTS content;"
	docker exec -it backend_admin python manage.py generate_test_data
	docker compose logs -f


up_api:
	echo "Поднимаю АПИ с ЕС и ЕТЛ"
	docker compose up -d --build backend_api es redis etl
	docker compose logs -f


# Remove all containers
kill_all_containers:
	docker compose down -v --remove-orphans

