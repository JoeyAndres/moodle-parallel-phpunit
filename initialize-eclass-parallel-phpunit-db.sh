#!/bin/bash

container="$1"

docker exec ${container} php /eclass-unified/admin/tool/phpunit/cli/init.php
