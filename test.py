# test.py

import operator
import pickle  # serializing

# local imports
import config
import const
import utility
import lang
from phpunit_container import phpunit_container_abstract
from phpunit_parallel_test import phpunit_parallel_test
        

def test(args):
    if '--help' in args:
        print """
        moodle-parallel-phpunit test [OPTIONS]

        Options:
        --stop-on-failure: Stops the test immediately after failure.

        --phpunit-master-dataroot [phpunit dataroot]:
                         Overrides the master's container phpunit dataroot.
                         This in turns override the slaves phpunit dataroot,
                         since they copy off the master's phpunit dataroot.

                         This is useful in dynamic build environments, where
                         phpunit dataroot could potentially change like Ant
                         build in Jenkins.

        --moodle-directory [moodle directory]:
                         Overrides the config.py's moodle_directory, which
                         is the path to the moodle instance we are testing.

                         This is useful in dynamic build environments, where
                         phpunit dataroot could potentially change like Ant
                         build in Jenkins.

        "moodle-parallel-phpunit test" requires running
        "moodle-parallel-phpunit setup [number of parallel tests]" before hand
        """
        return const.OK

    utility.handle_option('--stop-on-failure',
                             args,
                             stop_on_failure_option_handler, "")

    if utility.handle_option('--phpunit-master-dataroot',
                             args,
                             phpunit_master_dataroot_option_handler,
                             lang.NO_VALID_MASTER_DATA_ROOT_ARGUMENT_MSG) is const.ERROR:
        return const.ERROR

    if utility.handle_option('--moodle-directory',
                             args,
                             moodle_directory_option_handler,
                             lang.NO_VALID_MOODLE_DIR_ARGUMENT_MSG) is const.ERROR:
        return const.ERROR
    
    testsuites = utility.extract_testsuites_from_phpunitxml()

    # Acquire the unittest exection time from last time.
    unitest_execution_time_file = open(config.unitest_execution_time_file, 'r')
    testsuites_time = pickle.load(unitest_execution_time_file)
    unitest_execution_time_file.close()

    container_constructor = lambda i: phpunit_container_abstract(
        config.slave_image_name,
        config.container_names[i],
        config.container_temp_result_files[i],
        True)
    
    containers = [container_constructor(i) for i in range(config.container_count)]

    # Empty all temporary result file.
    [utility.empty_file(f) for f in config.container_temp_result_files]

    # Run and block while test is running.
    parallel_phpunit_test = phpunit_parallel_test(
        testsuites, containers, testsuites_time)
    parallel_phpunit_test.stop_on_failure = config.stop_on_failure
    parallel_phpunit_test.run().wait()

    # Merge all the results and remove all temporary result.
    utility.merge_files(config.container_temp_result_files, config.result_file)
    utility.rm_files(config.container_temp_result_files)

    serialize_testsuites_execution_time(parallel_phpunit_test.testsuites_time)

    result = const.OK
    for passed in parallel_phpunit_test.passed.values():
        if passed is False:
            result = const.ERROR
            break

    # Print total phpunit results.
    print_complete_phpunit_results()

    # Print any failed testsuites if any.
    print "\n"
    print_failed_testsuites(parallel_phpunit_test.failed_testsuites)
    print "\n"

    return result


"""
Serializes the testsuites_time for both machine and human. This
will aid in achieving *optimal testing time next time around.

*Note: Optimal is achieved if testsuites execution time didn't change
    much next test run.

@type dict
@param testsuites_time A mapping from testsuite to execution time.
"""
def serialize_testsuites_execution_time(testsuites_time):
    sorted_testsuites_time = sorted(testsuites_time.items(),
                                    key=operator.itemgetter(1))

    # Non-human readable version.
    unitest_execution_time_file = open(config.unitest_execution_time_file, 'w')
    pickle.dump(testsuites_time, unitest_execution_time_file)
    unitest_execution_time_file.close()

    # Human readable version.
    exec_time_lines = ["{0} {1}\n".format(testsuite, time)
                       for (testsuite, time) in sorted_testsuites_time]
    unitest_execution_time_str = "".join(exec_time_lines)
    unitest_execution_time_hr_file = open(config.unitest_execution_time_file_hr, 'w')
    unitest_execution_time_hr_file.write(unitest_execution_time_str)


"""
Print the final merge results.
"""
def print_complete_phpunit_results():
    result_file = open(config.result_file, 'r')
    print result_file.read()  # Output the file.


"""
Print the failed testsuites.

@type list
@param failed_testsuites list of failed testsuites.
"""
def print_failed_testsuites(failed_testsuites):
    if len(failed_testsuites) > 0:
        print "Failed testsuites: "
        for testsuite in failed_testsuites:
            print " * ", testsuite, '\n'


"""
Handler for --stop-on-failure option
@see utility.handle_option
"""
def stop_on_failure_option_handler(option, arg_list, arg_index):
    config.stop_on_failure = True


"""
Handler for --phpunit-master-dataroot option
@see utility.handle_option
"""
def phpunit_master_dataroot_option_handler(option, arg_list, arg_index):
    config.master_container_phpunit_dataroot = arg_list[arg_index]


"""
Handler for --moodle-directory option
@see utility.handle_option
"""
def moodle_directory_option_handler(option, arg_list, arg_index):
    config.moodle_directory = arg_list[arg_index]