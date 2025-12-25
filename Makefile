.PHONY: up down test build

up:
	docker-compose up --build -d

down:
	docker-compose down

test:
	pytest -q

build:
	docker build -t kasparro-backend .
