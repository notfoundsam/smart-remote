ALL: up-dev
build-dev:
	docker-compose -f docker-compose.yml build
build-server:
	docker-compose -f docker-compose-server.yml build
up:
	nohup python3 run.py > output.log &
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
ps:
	ps ax | grep 'python3 run.py'
kill:
	kill $(ps ax | grep '[p]ython3 run.py' | awk '{print $1}')
log:
	tail -F app.log
