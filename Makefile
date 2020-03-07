# based on http://www.slideshare.net/atteroTheGreatest/docker-in-everyday-development

.PHONY: build push shell python

build: Dockerfile
	docker build -t graphhopper/load-testing .

push: build
	docker push graphhopper/load-testing:latest

shell:
	docker run -it graphhopper/load-testing bash

python:
	docker run -it graphhopper/load-testing python
