#!/bin/bash

container="$1"
testsuites="$2"
container_result_file="$3"


test_output="$(docker exec ${container} /home/lmsadmin/run_phpunit_testsuites_subset.sh $testsuites)"
echo $test_output >> $container_result_file 2>&1  # Output for the file.
echo $test_output  # Output for terminal.
