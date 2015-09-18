#!/bin/bash

container="$1"
testsuites="$2"
container_result_file="$3"


test_output="$(docker exec -u lmsadmin ${container} /home/lmsadmin/run_phpunit_testsuites_subset.sh $testsuites)"
test_output="${test_output}\n"
echo -e "$test_output" >> $container_result_file 2>&1  # Output for the file.
echo -e "$test_output"  # Output for terminal.
