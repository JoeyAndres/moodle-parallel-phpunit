#!/bin/bash

image="$1"
container="$2"
moodle_instance_dir="$3"
other_options="$4"

docker run -d -v ${moodle_instance_dir}:/moodle-instance $other_options --name ${container} ${image}
