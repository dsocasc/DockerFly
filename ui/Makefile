# Makefile

IMAGE_NAME  = repo-clone-web-ui
DOCKERFILE_PATH = ./devops/Dockerfile
CONFIG_FILE_PATH = ../config.yml

# Read values from config.yml
EXPOSED_PORT := $(shell yq eval '.ui.exposed_port' $(CONFIG_FILE_PATH))
NETWORK_NAME := $(shell yq eval '.docker.network_name' $(CONFIG_FILE_PATH))
URL := $(shell yq eval '.ui.url' $(CONFIG_FILE_PATH))

build:
	docker build \
				-t $(IMAGE_NAME) \
				-f $(DOCKERFILE_PATH) \
				--build-arg URL=$(URL) \
				.

run: build
	docker run \
		-d \
		--name $(IMAGE_NAME) \
		-p $(EXPOSED_PORT):80 \
		--network=$(NETWORK_NAME) \
		$(IMAGE_NAME)

clean:
	docker stop $(IMAGE_NAME) && \
	docker rm $(IMAGE_NAME)