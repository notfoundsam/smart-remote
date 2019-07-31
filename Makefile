ALL: up-dev
build-dev:
	docker-compose -f docker-compose.yml build
build-server:
	docker-compose -f docker-compose-server.yml build
up-dev:
	docker-compose -f docker-compose.yml up -d
up-server:
	docker-compose -f docker-compose-server.yml up -d
stop:
	docker-compose stop
migrate:
	docker-compose exec web alembic upgrade +1
rollback:
	docker-compose exec web alembic downgrade -1
migrate-all:
	docker-compose exec web alembic upgrade head
rollback-all:
	docker-compose exec web alembic downgrade base
