# Makefile

IMAGE_NAME  = repo-clone-web-ui
DOCKERFILE_PATH = ./devops/Dockerfile
CONFIG_FILE_PATH = ../config.yml

# Read values from config.yml
EXPOSED_PORT := $(shell yq '.ui.exposed_port' $(CONFIG_FILE_PATH))

build:
	docker build \
				-t $(IMAGE_NAME) \
				-f $(DOCKERFILE_PATH) \
				--build-arg EXPOSED_PORT=$(EXPOSED_PORT) \
				.

run: build
	docker run \
		-d \
		--name $(IMAGE_NAME) \
		-p $(EXPOSED_PORT):80 \
		--network=nginx-proxy-net \
		$(IMAGE_NAME)

clean:
	docker stop $(IMAGE_NAME) && \
	docker rm $(IMAGE_NAME)