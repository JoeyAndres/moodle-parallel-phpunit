# config.py

import os


container_base_directory = os.path.dirname(__file__)  # This config.py should not be moved then.
data_directory = container_base_directory + '/data'
temp_directory = data_directory + '/tmp'
moodle_directory = "/home/jandres/CompScie/eclass-unified-docker"
moodle_phpunitxml_file = moodle_directory + "/phpunit.xml"

# Base container image. See ./Dockerfiles directory for more info.
master_image_name = 'eclass-parallel-phpunit-first'
slave_image_name = 'eclass-parallel-phpunit-rest'

# Template for container names.
container_name_template = 'eclass-parallel-phpunit-{0}'

# Ideally the number of cores.
container_count = 8

container_phpunit_dir_template = temp_directory + '/{0}'

# Temporary results. This {0} is meant to be the name of the container
# this result is from.
container_temp_result_file_template = temp_directory + '/{0}-result.out'

# Result of the phpunit test. Final output.
result_file = data_directory + '/result.out'

backup_file = data_directory + '/phpu_moodledb.sql'

# File containining "testsuite [time in seconds]" for each line.
# This is created so the next phpunit can use this for optimization purposes.
# unitest_execution_time_file is for program use only, the
# unitest_execution_time_file_hr is human readable version.
unitest_execution_time_file = data_directory + '/unittest-execution-time.out'
unitest_execution_time_file_hr = data_directory + '/unittest-execution-time-hr.out'

dockerfile_directory = container_base_directory + '/Dockerfiles'
slave_dockerfile = dockerfile_directory + '/dockerfile-first'
master_dockerfile = dockerfile_directory + '/dockerfile-rest'
