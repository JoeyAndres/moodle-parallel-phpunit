#!/bin/bash

container="$1"
backup_filename="$2"

(docker exec -u postgres "${container}" pg_dump -Fc moodledb) > "$backup_filename"
