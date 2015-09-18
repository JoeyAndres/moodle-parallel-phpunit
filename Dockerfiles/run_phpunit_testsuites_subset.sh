#!/usr/bin/env bash

# Runs a given portion of phpunit testsuites
# @param list of phpunit_testsuites (These are space separated, so quote them).

if [ -z "$1" ] ; then
    echo "Please provide the list of testsuites to run."
    exit
fi

testsuites=($1)  # No need to quote, we have taken care of undesired values.

for testsuite in ${testsuites[@]}; do
    /moodle-instance/vendor/bin/phpunit -c /moodle-instance/phpunit.xml --testsuite $testsuite
done
