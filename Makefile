test:
	CONFIG_PATH=settings/test/conf.yml pytest -v tests/

local-db:
	docker compose up -d postgres

web:
	CONFIG_PATH=settings/dev/conf.yml docker compose up -d web --build

teardown-local-db:
	docker compose down postgres

teardown-web:
	docker compose down web

up:
	CONFIG_PATH=settings/dev/conf.yml docker compose up -d --build

down:
	docker compose down

local-run:
	CONFIG_PATH=settings/local/conf.yml sh ./entrypoint.sh
