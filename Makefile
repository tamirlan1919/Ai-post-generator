.PHONY: up rebuild down logs logs-all shell db-shell migrate revision current restart clean

up:
	docker compose up -d

rebuild:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f api

logs-all:
	docker compose logs -f

shell:
	docker compose exec api bash

db-shell:
	docker compose exec postgres psql -U postgres -d aibot

migrate:
	docker compose run --rm --no-deps api alembic upgrade head

revision:
	docker compose run --rm --no-deps api alembic revision --autogenerate -m "$(m)"

current:
	docker compose run --rm --no-deps api alembic current

restart:
	docker compose restart api

clean:
	docker compose down -v
