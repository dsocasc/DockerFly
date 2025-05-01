FROM python:3.9-slim

# Define build arguments
ARG EXPOSED_PORT=8000
ARG REPO_PATH=/app
ARG URL=""

# Set environment variables
ENV EXPOSED_PORT=${EXPOSED_PORT}
ENV REPO_PATH=${REPO_PATH}

ENV VIRTUAL_HOST=${URL}
ENV VIRTUAL_PORT=${EXPOSED_PORT}

WORKDIR /app/

COPY resources/requirements.txt .

RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src
COPY main.py ./main.py

EXPOSE ${EXPOSED_PORT}