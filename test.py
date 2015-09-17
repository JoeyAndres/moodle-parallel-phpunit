# test.py

import os
import re  # regex
import operator
import pickle  # serializing

# local imports
import config
import const
import utility
from phpunit_container import phpunit_container_abstract
from phpunit_parallel_test import phpunit_parallel_test
        

def test(args):
    if '--help' in args:
        print """
        "eclass-parallel-phpunit test" requires running 
        "eclass-parallel-phpunit setup [number of parallel tests]" before hand"
        """
        return const.ERROR
    
    testsuites = utility.extract_testsuites_from_phpunitxml()

    # Acquire the unittest exection time from last time.
    unitest_execution_time_file = open(config.unitest_execution_time_file, 'r')
    testsuites_time = pickle.load(unitest_execution_time_file)
    unitest_execution_time_file.close()
    
    container_constructor = lambda index: phpunit_container_abstract(
        config.slave_image_name,
        config.container_name_template.format(index),
        config.container_temp_result_file_template.format(
            config.container_name_template.format(index)),
        True)
    
    containers = [container_constructor(i) for i in range(config.container_count)]
    container_temp_result_files = [
        config.container_temp_result_file_template.format(container.name)
        for container in containers ]

    # Empty all temporary result file.
    [utility.empty_file(f) for f in container_temp_result_files]

    # Run and block while test is running.
    test = phpunit_parallel_test(testsuites, containers, testsuites_time)
    test.run().wait()

    # Merge all the results and remove all temporary result.
    utility.merge_files(container_temp_result_files, config.result_file)
    utility.rm_files(container_temp_result_files)

    # Sort the output for human readable purposes.
    sorted_testsuites_time = sorted(test.testsuites_time.items(),
                                    key=operator.itemgetter(1))
    
    # Write testsuites execution time to file.
    ## Non-human readable version.
    unitest_execution_time_file = open(config.unitest_execution_time_file, 'w')
    pickle.dump(test.testsuites_time, unitest_execution_time_file)
    unitest_execution_time_file.close()
    ## Human readable version.
    exec_time_lines = ["{0} {1}\n".format(testsuite, time)
                       for (testsuite, time) in sorted_testsuites_time]
    unitest_execution_time_str = "".join(exec_time_lines)
    unitest_execution_time_hr_file = open(config.unitest_execution_time_file_hr, 'w')
    unitest_execution_time_hr_file.write(unitest_execution_time_str)

    result = const.OK
    for passed in test.passed.values():
        if passed is False:
            result = const.ERROR

    # Print any failed testsuites if any.
    if len(test.failed_testsuites) > 0:
        print "Failed testsuites: "
        for testsuite in test.failed_testsuites:
            print " * ", testsuite, "\n"

    result_file = open(config.result_file, 'r')
    print result_file.read()  # Output the file.
    
    return result

# Solution, Wrap test in class. Have a thread for each test. Give each thread
# function. Have test class lock an array when acessing it.
