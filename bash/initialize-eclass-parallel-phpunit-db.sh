#!/bin/bash

container="$1"

docker exec -u lmsadmin ${container} php /moodle-instance/admin/tool/phpunit/cli/init.php
