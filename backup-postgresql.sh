#!/bin/bash

container="$1"

(docker exec -u postgres ${container} pg_dump moodledb) > phpu_moodledb.sql