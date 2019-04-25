.PHONY: build up

clean:
	docker-compose -f docker/docker-compose.yml rm -f

build:
	docker-compose -f docker/docker-compose.yml build

up:
	docker-compose -f docker/docker-compose.yml up -d

down:
	docker-compose -f docker/docker-compose.yml down

stop:
	docker-compose -f docker/docker-compose.yml stop

shell:
	docker-compose -f docker/docker-compose.yml exec frisbeer-backend bash
