# Makefile

IMAGE_NAME  = repo-clone-server
DOCKERFILE_PATH = ./devops/Dockerfile
CONFIG_FILE_PATH = ../config.yml

# Read values from config.yml
EXPOSED_PORT := $(shell yq  '.server.exposed_port' $(CONFIG_FILE_PATH))
REPO_PATH := $(shell yq  '.server.repositories_clone_path' $(CONFIG_FILE_PATH))
NETWORK_NAME := $(shell yq  '.docker.network_name' $(CONFIG_FILE_PATH))
URL := $(shell yq  '.server.url' $(CONFIG_FILE_PATH))

ifeq ($(EXPOSED_PORT),)
$(error ERROR: Could not read .server.exposed_port from $(CONFIG_FILE_PATH). Is yq (python wrapper) installed and is the config file correct?)
endif
ifeq ($(REPO_PATH),)
$(error ERROR: Could not read .server.repositories_clone_path from $(CONFIG_FILE_PATH).)
endif
ifeq ($(NETWORK_NAME),)
$(error ERROR: Could not read .docker.network_name from $(CONFIG_FILE_PATH).)
endif

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