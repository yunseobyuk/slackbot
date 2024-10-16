app-build:
	docker-compose build

app-up:
	docker-compose up -d

app-down:
	docker-compose down

app-restart:
	docker restart slackbot

code-beauty:
	black . && isort .

app-log:
	docker logs -t -f slackbot

pip-list:
	docker-compose exec app pip list
