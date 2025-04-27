FROM python:3.9-slim

WORKDIR /app

COPY resources/requirements.txt .

RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean

RUN pip install --no-cache-dir -r requirements.txt

COPY ./resources/config.yml ./resources/config.yml
COPY ./src ./src
COPY main.py ./main.py

EXPOSE 8000
