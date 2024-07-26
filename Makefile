install:
	poetry install

lint:
	poetry run flake8 engine

start:
	poetry run guild-manager-bot
