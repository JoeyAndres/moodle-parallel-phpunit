#!/bin/bash

image="$1"
container="$2"
eclass_dir="$3"
other_options="$4"

docker run -d -v ${eclass_dir}:/eclass-unified $other_options --name ${container} ${image}
