#!/bin/bash

jobs_exist=true

while [ $jobs_exist = true ]; do
    jobs=$(jobs)
    if [ -z "$jobs" ]; then
	echo "No more jobs."
	jobs_exist=false
    else
	echo "Waiting for jobs: $jobs"
	jobs_exist=true
    fi
    
    sleep 2s  # Avoid fast polling.
done
