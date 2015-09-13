# test.py

import os
import re  # regex

# local imports
import divide_testsuites

def test(args):
    # TODO: Encapsulates these in a module and return, don't exit. Let the call deal with the return.
    # TODO: Have a function to chck if .config exist, if .config is valid, container corresponding
    #       to .config exist.
    if '--help' in args:
        print "\"eclass-parallel-phpunit test\" requires running \"eclass-parallel-phpunit setup [number of parallel tests]\" before hand"
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

    for instance_number in range(phpunit_instance_count):
        container = "{0}-{1}".format("eclass-parallel-phpunit", instance_number)
        print "Creating {0}".format(container)
        
        test_cmd = "./test-eclass-parallel-phpunit.sh {0} \"{1}\"".format(
            container, " ".join(testsuites_group_array[instance_number]))
        print test_cmd
        
        os.system(test_cmd)
