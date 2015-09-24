#!/bin/bash

container="$1"

pgsql_running=false

while [ "$pgsql_running" = false ]; do
    pgsql_online_status=$(docker exec "${container}" service postgresql status | grep online)
    echo "$pgsql_online_status"
    if [ -z "$pgsql_online_status" ]; then
	echo "Waiting for postgresql to start."
	pgsql_running=false
    else
	echo "postgresql is now starting. Much speed WOW."
	pgsql_running=true
    fi
    
    sleep 2s  # Avoid fast polling.
done
