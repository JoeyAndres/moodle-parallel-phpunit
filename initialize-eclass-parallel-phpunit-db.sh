#!/bin/bash

container="$1"

sudo docker exec -u lmsadmin ${container} php /eclass-unified/admin/tool/phpunit/cli/init.php
