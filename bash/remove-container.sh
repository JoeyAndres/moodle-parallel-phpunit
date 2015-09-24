#!/bin/bash

CONTAINER_NAME=$1

echo "Container: $CONTAINER_NAME";

# See if the container is running. If so, stop and remove it.
                          
EXIST=`docker ps -a | grep "[[:space:]]${CONTAINER_NAME}$"`
if [ -n "$EXIST" ]; then
    echo "Container already exist, and maybe running. This will be stopped and removed."
    docker stop "$CONTAINER_NAME"
    docker rm "$CONTAINER_NAME"
fi
