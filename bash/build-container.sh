#!/bin/bash

container_name="$1"
docker_file="$2"
docker_file_directory="$3"

docker build -t "${container_name}" -f "${docker_file}" "${docker_file_directory}"
