VERSION = 0.1.0

PACKAGE = nginx_statsd_sidecar

DOCKER_REGISTRY = caltechads/nginx_statsd_sidecar

#======================================================================

clean:
	rm -rf *.tar.gz dist *.egg-info *.rpm
	find . -name "*.pyc" -exec rm '{}' ';'

dist: clean
	@python setup.py sdist
	@python setup.py bdist_wheel --universal

release: dist
	@twine upload dist/*

build:
	docker build -t ${PACKAGE}:${VERSION} .
	docker tag ${PACKAGE}:${VERSION} ${PACKAGE}:latest
	docker image prune -f

force-build: aws-login
	docker build --no-cache -t ${PACKAGE}:${VERSION} .
	docker tag ${PACKAGE}:${VERSION} ${PACKAGE}:latest

tag:
	docker tag ${PACKAGE}:${VERSION} ${DOCKER_REGISTRY}/${PACKAGE}:${VERSION}
	docker tag ${PACKAGE}:latest ${DOCKER_REGISTRY}/${PACKAGE}:latest

push: tag
	docker push ${DOCKER_REGISTRY}/${PACKAGE}

pull:
	docker pull ${DOCKER_REGISTRY}/${PACKAGE}:${VERSION}

dev:
	docker-compose up

dev-detached:
	docker-compose up -d

devdown:
	docker-compose down

restart:
	docker-compose restart nginx_statsd_sidecar

exec:
	docker exec -it nginx_statsd_sidecar /bin/bash

log:
	docker-compose logs -f nginx_statsd_sidecar

logall:
	docker-compose logs -f

docker-clean:
	docker stop $(shell docker ps -a -q)
	docker rm $(shell docker ps -a -q)

docker-destroy: docker-clean docker-destroy-db
	docker rmi -f $(shell docker images -q | uniq)
	docker image prune -f; docker volume prune -f; docker container prune -f
