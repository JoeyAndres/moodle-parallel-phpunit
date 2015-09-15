#!/bin/bash

# Precondition(s):
# - /phpu_moodledata/phpu_moodledb.sql exist already.

container="$1"

docker exec -i -u postgres ${container} pg_restore -j 16 -d moodledb /phpu_moodledata/phpu_moodledb.sql
