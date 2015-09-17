# setup.py

import os
import os.path
import time
import sys
import subprocess
import pickle

# Local
from phpunit_container import phpunit_container_master, phpunit_container_slave
import utility
import config
import const


"""
Recreate the docker images for both master/first and slaves/rest.
"""
def recreate_image():
    print "Creating eclass-parallel-phpunit-first image\n"
    utility.build_container('eclass-parallel-phpunit-first',
                            config.master_dockerfile,
                            config.dockerfile_directory)
    
    print "Creating eclass-parallel-phpunit-rest image\n"
    utility.build_container('eclass-parallel-phpunit-rest',  # todo: Transfer this to config.py
                            config.slave_dockerfile,
                            config.dockerfile_directory)

"""
Starts the docker containers.

@throws
"""
def start_container():
   pass 

    
"""
"""
def setup(args):
    if '--help' in args:
        print """
        Prior to calling "eclass-parallel-phpunit setup", ensure that config.py's
        parameters are properly set with your environment.
        """
        return const.OK
        
    if '--recreate-image' in args:
        recreate_image()

    if '--start-containers' in args:
        start_container()

    only_update_slaves = False
    if '--only-update-slaves' in args:
        only_update_slaves = True
        
        
    # Create the master container obj.
    master_container_name = config.container_name_template.format(0)
    result_file = config.container_temp_result_file_template.format(
        master_container_name)
    master_container = phpunit_container_master(config.master_image_name,
                                                master_container_name,
                                                result_file,
                                                True)
    containers = [master_container]  # Reference to all containers.
    
    master_routine = lambda: [
        master_container.remove_if_exist(),
        master_container.create(),
        master_container.init_phpunit_db() ]
    
    if only_update_slaves is False:
        print("--- {0}s seconds ---".format(utility.execute_and_time(master_routine)))

    # Create the slave obj(s).
    for instance_number in range(1, config.container_count):
        container_name = config.container_name_template.format(instance_number)
        result_file = config.container_temp_result_file_template.format(
            container_name)
        slave_container = phpunit_container_slave(config.slave_image_name,
                                                  container_name,
                                                  master_container,
                                                  result_file,
                                                  True)
        containers.append(slave_container)

        slave_routine = lambda: [
            slave_container.remove_if_exist(),
            slave_container.create(),
            slave_container.init_phpunit_db() ]
        print("--- {0}s seconds ---".format(utility.execute_and_time(slave_routine)))

    # Check if "execution time file" exist.
    execution_time_file_exist = os.path.isfile(config.unitest_execution_time_file)
    if execution_time_file_exist is False:
        # Initialize the execution time. Since we have not executed any test yet,
        # Just place 666 as estimates for execution time.
        testsuites = utility.extract_testsuites_from_phpunitxml()
        exec_time = 666
        unittest_execution_times = dict(
            [(testsuite, exec_time) for testsuite in testsuites])
        unitest_execution_time_file = open(config.unitest_execution_time_file, 'w')
        pickle.dump(unittest_execution_times, unitest_execution_time_file)

    return const.OK
