#!/bin/bash

# Check if all required parameters are provided
IMAGE_NAME=$1
EXPOSED_PORT=$2
DIR_PATH=$3
NETWORK_NAME=$4

if [ -z "$IMAGE_NAME" ] || [ -z "$EXPOSED_PORT" ] || [ -z "$DIR_PATH" ]; then
    echo "Error: All parameters are required"
    echo "Usage: $0 IMAGE_NAME EXPOSED_PORT REPO_PATH"
    exit 1
fi

# Create the directory if it doesn't exist
if [[ ! -d "$DIR_PATH" ]]; then
    echo "Creating directory: $DIR_PATH"
    mkdir -p "$DIR_PATH"
else
    echo "Directory already exists: $DIR_PATH"
fi

# Run FastAPI application
echo "Starting FastAPI application..."
docker run \
    -d \
    --name $IMAGE_NAME \
    -p $EXPOSED_PORT:$EXPOSED_PORT \
    -v $DIR_PATH:$DIR_PATH \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --network=$NETWORK_NAME \
    $IMAGE_NAME \
    bash -c "uvicorn main:app --host 0.0.0.0 --port $EXPOSED_PORT"
