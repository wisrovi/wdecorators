.PHONY: build up down logs restart


build:
	@echo "Generando .env..."
	sh ./generator.sh

start:
	docker compose -f docker-compose.yml --env-file graylog.env   up -d

down:
	docker compose -f docker-compose.yml down

logs:
	docker compose -f docker-compose.yml logs -f

restart: down start
