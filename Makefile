.PHONY: build up

clean:
	docker-compose -f docker/docker-compose.yml rm -f

build:
	docker-compose -f docker/docker-compose.yml build

up:
	docker-compose -f docker/docker-compose.yml up