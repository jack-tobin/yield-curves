test:
	CONFIG_PATH=settings/test/conf.yml pytest -v tests/

local-db:
	docker compose up -d postgres

web:
	CONFIG_PATH=settings/prod/conf.yml docker compose up -d web --build

teardown-local-db:
	docker compose down postgres

teardown-web:
	docker compose down web

up:
	CONFIG_PATH=settings/prod/conf.yml docker compose up -d --build

local:
	CONFIG_PATH=settings/local/conf.yml docker compose up -d --build

down:
	docker compose down

local-run:
	CONFIG_PATH=settings/local/conf.yml sh ./entrypoint.sh

local-run-prod:
    CONFIG_PATH=settings/prod/conf.yml sh ./entrypoint.sh

get-bund-data:
	python -m src.manage runscript get_bund_data

local-redis:
	docker compose up -d redis

teardown-local-redis:
	docker compose down redis

migrate:
	CONFIG_PATH=settings/prod/conf.yml python -m src.manage migrate

migrate-local:
	CONFIG_PATH=settings/local/conf.yml python -m src.manage migrate

shell:
	CONFIG_PATH=settings/prod/conf.yml python -m src.manage shell
