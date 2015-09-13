#!/bin/bash

container="$1"
testsuites="$2"


(sudo docker exec -u lmsadmin ${container} \
      /home/lmsadmin/run_phpunit_testsuites_subset.sh "\"$testsuites\"") > ${container}-result.out &
