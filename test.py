# test.py

import os
import re  # regex
from threading import Thread

# local imports
import divide_testsuites
from phpunit_container import phpunit_container_abstract


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

    image_name = 'eclass-parallel-phpunit'
    container_name_template = 'eclass-parallel-phpunit-{0}'
    containers = [phpunit_container_abstract(image_name,
                                             container_name_template.format(i),
                                             True)
                  for i in range(phpunit_instance_count)]

    thread_array = []
    for instance_number in range(phpunit_instance_count):
        container = "{0}-{1}".format("eclass-parallel-phpunit", instance_number)
        print "Creating {0}".format(container)

        test_routine = lambda: containers[instance_number].tests(testsuites_group_array[instance_number])
        # Spawn in a separate thread. This is the key to parallel execution.
        thread_instance = Thread(None,  test_routine)
        thread_array.append(thread_instance)
        thread_instance.daemon = True
        thread_instance.start()

    # Ensure that all thread terminates.
    for thread in thread_array:
        print "Waiting for thread: {0}".format(thread.name)
        thread.join()
