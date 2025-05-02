# Makefile

IMAGE_NAME  = repo-clone-server
DOCKERFILE_PATH = ./devops/Dockerfile
CONFIG_FILE_PATH = ../config.yml

# Read values from config.yml
EXPOSED_PORT := $(shell yq eval '.server.exposed_port' $(CONFIG_FILE_PATH))
REPO_PATH := $(shell yq eval '.server.repositories_clone_path' $(CONFIG_FILE_PATH))
NETWORK_NAME := $(shell yq eval '.docker.network_name' $(CONFIG_FILE_PATH))
URL := $(shell yq eval '.server.url' $(CONFIG_FILE_PATH))


build:
	docker build \
				-t $(IMAGE_NAME) \
				-f $(DOCKERFILE_PATH) \
				--build-arg EXPOSED_PORT=$(EXPOSED_PORT) \
				--build-arg REPO_PATH=$(REPO_PATH) \
				--build-arg URL=$(URL) \
				.

run: build
	./devops/container_run.sh $(IMAGE_NAME) $(EXPOSED_PORT) $(REPO_PATH) $(NETWORK_NAME)

clean:
	docker stop $(IMAGE_NAME) && \
	docker rm $(IMAGE_NAME)