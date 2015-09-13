#!/bin/bash

container="$1"
log_file="logs/restore-${container}.log"

cat "Restore Log: $(date)" >> $log_file
(cat ./phpu_moodledb.sql | docker exec -i -u postgres ${container} psql moodledb) >> $log_file 2>&1
