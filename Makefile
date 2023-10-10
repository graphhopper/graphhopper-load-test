# based on http://www.slideshare.net/atteroTheGreatest/docker-in-everyday-development

.PHONY: build push shell python

build: Dockerfile
	docker build -t graphhopper/load-testing .

push: build
	docker push graphhopper/load-testing:latest

push-amd64:
	docker buildx build -t graphhopper/load-testing:latest --platform=linux/amd64 --push .

shell:
	docker run -it -v ${PWD}:/app graphhopper/load-testing bash

python:
	docker run -it -v ${PWD}:/app graphhopper/load-testing python
