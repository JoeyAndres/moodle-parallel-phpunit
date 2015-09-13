#!/bin/bash

container="$1"

docker exec -u lmsadmin ${container} php /eclass-unified/admin/tool/phpunit/cli/init.php
