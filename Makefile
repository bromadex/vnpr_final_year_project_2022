.PHONY: help build up down logs migrate shell test clean

help:
	@echo "VNPR - Available commands:"
	@echo "  make build    - Build all Docker images"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - View logs"
	@echo "  make migrate  - Run database migrations"
	@echo "  make shell    - Open Django shell"
	@echo "  make test     - Run tests"
	@echo "  make clean    - Remove all containers and volumes"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

migrate:
	docker-compose exec backend python manage.py migrate

shell:
	docker-compose exec backend python manage.py shell

test:
	docker-compose exec backend python manage.py test

clean:
	docker-compose down -v --rmi all
