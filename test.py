# test.py

import os
import re  # regex

# local imports
import config
import divide_testsuites
from phpunit_container import phpunit_container_abstract
from phpunit_parallel_test import phpunit_parallel_test
        

def test(args):
    # TODO: Encapsulates these in a module and return, don't exit. Let the call deal with the return.
    # TODO: Have a function to chck if .config exist, if .config is valid, container corresponding
    #       to .config exist.
    if '--help' in args:
        print """
        "eclass-parallel-phpunit test" requires running 
        "eclass-parallel-phpunit setup [number of parallel tests]" before hand"
        """
        sys.exit(1)

    config_file = open(".config", 'r')
    config_str = config_file.read().decode('utf-8')
    container_count_regex = re.search("container-count: ([0-9]+)", config_str)
    print container_count_regex
    phpunit_instance_count = (int)(container_count_regex.group(1))
    print "container-count: {0}".format(phpunit_instance_count)

    # TODO: Have a way to acquire the phpunit.xml (save the directory on create container).
    testsuites_group_array = divide_testsuites.divide_testsuites(
        './phpunit.xml', phpunit_instance_count)
    testsuites = divide_testsuites.divide_testsuites('./phpunit.xml', 1)[0]

    image_name = 'eclass-parallel-phpunit'
    container_name_template = 'eclass-parallel-phpunit-{0}'
    # TODO: Place container name in a config file.
    containers = [phpunit_container_abstract(image_name,
                                             container_name_template.format(i),
                                             True,
                                             container_name_template.format(i) + '-result.out')
                  for i in range(phpunit_instance_count)]

    for container_index in range(phpunit_instance_count):
        print "Clearing {0}-result.out".format(containers[container_index].container_name)
        os.system('echo '' > {0}'.format(
            containers[container_index].container_name + '-result.out'))
    
    test = phpunit_parallel_test(testsuites, containers)
    test.run().wait()

    os.system('cat {0} > result.out'.format(
        containers[0].container_name + '-result.out'))
    os.system('rm {0}'.format(containers[0].container_name + '-result.out'))

    for container_index in range(1, phpunit_instance_count):
        os.system('cat {0} >> result.out'.format(
            containers[container_index].container_name + '-result.out'))
        os.system('rm {0}'.format(
            containers[container_index].container_name + '-result.out'))

    # Sort the output for human readable purposes.
    import operator
    sorted_testsuites_time = sorted(test.testsuites_time.items(), key=operator.itemgetter(1))
    
    unitest_execution_time_str = ""
    for (testsuite, time) in sorted_testsuites_time:
        unitest_execution_time_str += "{0} {1}\n".format(testsuite, time)
        
    unitest_execution_time_file = open(config.unitest_execution_time_file, 'w')
    unitest_execution_time_file.write(unitest_execution_time_str)

# Solution, Wrap test in class. Have a thread for each test. Give each thread
# function. Have test class lock an array when acessing it.
