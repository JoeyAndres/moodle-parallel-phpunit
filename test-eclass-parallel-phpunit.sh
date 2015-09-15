#!/bin/bash

container="$1"
testsuites="$2"
container_result_file="$3"


(docker exec -u lmsadmin ${container} /home/lmsadmin/run_phpunit_testsuites_subset.sh $testsuites) >> $container_result_file 2>&1
