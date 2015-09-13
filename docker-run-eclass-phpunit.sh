#!/bin/bash

image="$1"
instance_count="$2"
eclass_dir="$3"
testsuites_subset="$4"

container="$image"-"$instance_count"
echo $container

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
"$DIR"/remove-container.sh "$container"

docker run -d -P -v ${eclass_dir}:/eclass-unified --name ${container} ${image}

# TODO: Have a clean way to know if db is up.
sleep 20s

(docker exec -u lmsadmin ${container} /home/lmsadmin/run_phpunit_testsuites_subset.sh "\"$testsuites_subset\"") > test-${instance_count}.out &
