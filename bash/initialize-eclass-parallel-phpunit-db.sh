#!/bin/bash

container="$1"

docker exec ${container} php /moodle-instance/admin/tool/phpunit/cli/init.php
