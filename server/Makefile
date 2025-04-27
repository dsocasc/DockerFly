# Makefile

IMAGE_NAME  = repo-clone-server
DOCKERFILE_PATH = ./devops/Dockerfile

build:
	docker build \
				-t $(IMAGE_NAME) \
				-f $(DOCKERFILE_PATH) .

run:
	docker run \
				-d \
				--name $(IMAGE_NAME) \
				-p 8000:8000 \
				$(IMAGE_NAME) \
				bash -c "fastapi run main.py" \
				-v ./share/:/share/