#!/bin/bash

container="$1"
log_file="logs/restore-${container}.log"

echo "Restore Log: $(date) ########################################################################" >> $log_file
docker exec -i -u postgres ${container} pg_restore -j 16 -d moodledb /phpu_moodledata/phpu_moodledb.sql
echo -e "\n"
