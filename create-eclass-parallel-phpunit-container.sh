#!/bin/bash

image="$1"
container="$2"
eclass_dir="$3"

sudo docker run -d -v ${eclass_dir}:/eclass-unified --name ${container} ${image}
