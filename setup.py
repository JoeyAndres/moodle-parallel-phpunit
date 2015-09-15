# setup.py

import os
import time
import sys
import subprocess

from phpunit_container import phpunit_container_master, phpunit_container_slave
import utility

"""
"""
def recreate_image():
    print "Creating eclass-parallel-phpunit-first image"
    create_docker_first_img_cmd = "docker build -t eclass-parallel-phpunit-first -f ./Dockerfiles/dockerfile-first ./Dockerfiles"

    print "Creating eclass-parallel-phpunit-rest image"
    create_docker_rest_img_cmd = "docker build -t eclass-parallel-phpunit -f ./Dockerfiles/dockerfile-rest ./Dockerfiles"
    os.system(create_docker_rest_img_cmd)

    
"""
"""
def setup(args):
    # TODO: Encapsulates these in a module and return, don't exit. Let the call deal with the return.
    if len(args) is 0:
        print """
        No arguments to command given. For more info execute: 
        "eclass-parallel-phpunit setup --help".
        """
        sys.exit(1)
        
    if '--help' in args:
        print """
        "eclass-parallel-phpunit setup" requires the number of parallel phpunit 
        instance to execute. The ideal number is the number of cores in your system. 
        For instance in an 8-core machine: "eclass-parallel-phpunit setup 8"
        """
    if '--recreate-image' in args:
        recreate_image()

    phpunit_instance_count = None
    try:
        phpunit_instance_count = int(args[0])
    except ValueError:
        print """
        Argument {0} given is not a positive integer. For more info execute: 
        "eclass-parallel-phpunit setup --help".
        """.format(args[0])
        sys.exit(1)

    # Save some data for other commands.
    config_str = '''
    container-count: {0}
    '''.strip().format(phpunit_instance_count)

    print config_str
    
    config_file = open(".config", 'w')
    config_file.write(config_str)

    image_name = 'eclass-parallel-phpunit'
    master_container = phpunit_container_master(image_name,
                                                'eclass-parallel-phpunit-0',
                                                True)
    containers = [master_container]  # Reference to all containers.
    
    master_routine = lambda: [
        master_container.remove_if_exist(),
        master_container.create(),
        master_container.init_phpunit_db() ]
    print("--- {0}s seconds ---".format(utility.execute_and_time(master_routine)))
    
    for instance_number in range(1, phpunit_instance_count):
        container_name = 'eclass-parallel-phpunit-{0}'.format(instance_number)
        slave_container = phpunit_container_slave(image_name,
                                                  container_name,
                                                  master_container, True)
        containers.append(slave_container)

        slave_routine = lambda: [
            slave_container.remove_if_exist(),
            slave_container.create(),
            slave_container.init_phpunit_db() ]
        print("--- {0}s seconds ---".format(utility.execute_and_time(slave_routine)))
