# setup.py

import os
import os.path
import pickle

# Local
from phpunit_container import phpunit_container_master, phpunit_container_slave
import utility
import config
import const
import lang

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
        moodle-parallel-phpunit setup [OPTIONS]

        Options:
        --create-image: Creates the image based off the config.py's
                        master/slave_image. Creating an image that
                        already exist simply replaces the older one.

        --only-update-slaves: This is meant to be for those using this tool
                         in personal machine in which there is a human that
                         knows there's no need for db update (no new plugin,
                         or new test files).

                         (Note: This is to be deprecated in Alpha release,
                                in which this checking will be automated.)
                         (Note: Pre-Alpha doesn't handle starting containers
                                if not yet started, so do it yourself atm.)

        Prior to calling "moodle-parallel-phpunit setup", ensure that config.py's
        parameters are properly set with your environment.
        """
        return const.OK

    if utility.handle_option('--create-image', args, create_image, "") is const.ERROR:
        return const.ERROR

    if utility.handle_option('--only-update-slaves',
                             args,
                             only_update_slaves_handler,
                             "") is const.ERROR:  # Boolean are reference.
        return const.ERROR

    # Create necessary directory(ies).
    create_necessary_directories()

    # Create the master container obj.
    result_file = config.container_temp_result_file_template.format(
        config.master_container_name)
    master_container = phpunit_container_master(config.master_image_name,
                                                config.master_container_name,
                                                result_file,
                                                True,
                                                config.master_container_phpunit_dataroot)

    if config.only_update_slaves is False:
        print("--- {0}s seconds ---".format(
            utility.execute_and_time(master_container.create_and_instantiate)))

    # Create the slave obj(s).
    [create_ith_slave_container(i, master_container)
     for i in range(1, config.container_count)]

    # Check if "execution time file" exist. If not, create one.
    initialize_execution_time_file()

    return const.OK


"""
Create necessary directories for this app to work.
"""
def create_necessary_directories():
    utility.mkdirs([ config.data_directory ])

"""
Recreate the docker images for both master/first and slaves/rest.
"""
def create_image(*args):
    print "Creating {0} image\n".format(config.master_image_name)
    utility.build_container(config.master_image_name,
                            config.master_dockerfile,
                            config.dockerfile_directory)

    print "Creating {0} image\n".format(config.slave_image_name)
    utility.build_container(config.slave_image_name,
                            config.slave_dockerfile,
                            config.dockerfile_directory)


"""
Handler for --only-update-slaves option
@see utility.handle_option
"""
def only_update_slaves_handler(option, arg_list, arg_index):
    config.only_update_slaves = True


"""
Initialize the execution file if it's not there already. It will be given
some exec time estimate.
"""
def initialize_execution_time_file():
    execution_time_file_exist = os.path.isfile(config.unitest_execution_time_file)
    if execution_time_file_exist is False:
        # Initialize the execution time. Since we have not executed any test yet,
        # Just place 666 as estimates for execution time.
        testsuites = utility.extract_testsuites_from_phpunitxml()
        exec_time = 666
        unittest_execution_times = dict([(testsuite, exec_time)
                                         for testsuite in testsuites])
        unitest_execution_time_file = open(config.unitest_execution_time_file, 'w')
        pickle.dump(unittest_execution_times, unitest_execution_time_file)

"""
Create the ith slave container.

@type int
@param ith The ith slave container. ith > 0 since master container is ith = 0.

@type phpunit_container_master
@param master_container Reference to the master container in which this constainer
                        is a slave to.
"""
def create_ith_slave_container(ith, master_container):
    assert ith > 0
    slave_container = phpunit_container_slave(
            config.slave_image_name,
            config.container_names[ith],
            master_container,
            config.container_temp_result_file_template[ith],
            True)
    print("--- {0}s seconds ---".format(utility.execute_and_time(
        slave_container.create_and_instantiate)))