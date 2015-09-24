"""
utility.py

This is where functions that belongs to a reasonably  size module. 

This is also the place for functions that uses "os.system" which are 
inherently UGLY.
"""

import time
import os
import subprocess
import re
import xml.etree.ElementTree as ET

# Local
import config
import const


"""
@type function|lambda
@param fn_or_lambda function or lambda to be executed and timed.

@type *args
@param *args Python's *args, (aka varargs). Dereferences a tuple if only args.

@return integer (s)
"""
def execute_and_time(fn_or_lambda, *args):
    start_time = time.time()
    fn_or_lambda(*args)
    end_time = time.time()
    return end_time - start_time

"""
@type function|lambda
@param fn_or_lambda function or lambda to be executed and timed.

@type *args
@param *args Python's *args, (aka varargs). Dereferences a tuple if only args.

@return (integer (s), return value of fn_or_lambda)
"""
def execute_and_time_with_return(fn_or_lambda, *args):
    start_time = time.time()
    rv = fn_or_lambda(*args)
    end_time = time.time()
    return (end_time - start_time, rv)


"""
"""
def extract_testsuites_from_phpunitxml(phpunitxml=config.moodle_phpunitxml_file):
    phpunit_xml_tree = ET.parse(phpunitxml)
    phpunit_xml_root = phpunit_xml_tree.getroot()

    testsuites_node = phpunit_xml_root[1];

    # Acquire all the testsuites and placed them in testsuites_arr.
    testsuites_arr=[]
    for testsuite_node in testsuites_node:
        # See if testsuite node have any child nodes (aka directory nodes).
        if len(testsuite_node) > 0:
            testsuites_arr.append(testsuite_node.get('name'))

    return testsuites_arr

"""
Clears the contents of the file.

@type string
@param file_path Path to the file to clear the contents of.
"""
def empty_file(file_path):
    os.system('echo "" > {0}'.format(file_path))

"""
Merges all the source_files to the dest_file.

@type List
@param source_files List of path of files to merge.

@type string
@param dest_file The path of the file in which all the source_files are merged.
"""
def merge_files(source_files, dest_file):
    # Create the dest_file first.
    os.system('echo "" > {0}'.format(dest_file))

    for source_file in source_files:
        os.system('cat {0} >> {1}'.format(source_file, dest_file))

"""
@type List
@param files List containing the path of files to remove.
"""
def rm_files(files):
    [os.system('rm {0}'.format(f)) for f in files]


"""
@type list
@param directories List of directories to create.
"""
def mkdirs(dirs):
    [os.system('mkdir -p {0}'.format(dir)) for dir in dirs]
               
        
def build_container(container_name, docker_file, docker_file_directory):
    cmd = "{0}/build-container.sh {1} {2} {3}".format(
        config.bash_files,
        container_name,
        docker_file,
        docker_file_directory)
    os.system(cmd)

"""
Starts the docker container.

@type string
@param container_name Name of the container to start.
"""
def start_container(container_name):
    cmd = "{0}/start-container.sh {1}".format(
        config.bash_files,
        container_name)
    os.system(cmd)

"""
Remove docker container if it exist. Nothing happens otherwise.

@type string
@param container_name Name of the container to remove.
"""
def remove_container(container_name):
    cmd = "{0}/remove-container.sh {1}".format(
        config.bash_files,
        container_name)
    os.system(cmd)

"""
Creates the container from a given image.

@type string
@param image_name Name of the image that is built already.

@type string
@param container_name Name of the container to create.

@type string
@param moodle_directory Path to the moodle directory. Defaults to the one in 
                        config.
"""
def create_container(image_name,
                     container_name,
                     moodle_directory=config.moodle_directory):
    extra_options = "\" -v {0}:/phpu_moodledata\"".format(
        config.container_phpunit_dataroot_template.format(container_name))
    cmd = "{0}/create-moodle-parallel-phpunit-container.sh {1} {2} {3} {4}".format(
        config.bash_files,
        image_name,
        container_name,
        moodle_directory,
        extra_options)
    os.system(cmd)

"""
Blocks when the given container name is loading.

@type string
@param container_name Name of the container to watch and block while
its database function.
"""
def block_while_initializing_db(container_name):
    os.system("{0}/block-until-db-starts.sh {1}".format(
        config.bash_files,
        container_name))

"""
Executes the given testsuite(s) in the given container and appends
its result in the result_file.

@type string
@param container_name Name of the container to run the unit test.

@type list
@param testsuites List of testsuite(s) to run.

@type string
@param result_file Path to the result file where the test results are appended.

@return True if no error, otherwise False.
"""
def run_phpunit_test(container_name, testsuites, result_file):
    if len(testsuites) is 1:
        cmd = "{0}/test-moodle-parallel-phpunit.sh {1} {2} {3}".format(
            config.bash_files,
            container_name,
            testsuites[0],
            result_file)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()

        match = re.search("There was [0-9]+ failure", out)
        no_error = match is None

        # todo: remove duplication.
        if no_error:
            return True
        else:
            return False
    elif len(testsuites) > 1:
        cmd = "{0}/test-moodle-parallel-phpunit.sh {1} \"{2}\" {3}".format(
            config.bash_files,
            container_name,
            " ".join(testsuites),
            result_file)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()

        match = re.search("There was [0-9]+ failure", out)
        no_error = match is None

        if no_error:
            return True
        else:
            return False
    # Otherwise nothing happens.

"""
Initialize the phpunit db of a given container. Specifically, executes:
php admin/tool/phpunit/cli/init.php

@type string
@param container_name Name of the container to initialize db.
"""
def initialize_phpunit_db(container_name):
    cmd = "{0}/initialize-moodle-parallel-phpunit-db.sh {1}".format(
        config.bash_files,
        container_name)
    os.system(cmd)

"""
Backup the phpunit db to a backup_file.

@type string
@param container_name Name of the container to backup the db of.
"""
def backup_phpunit_db(container_name, backup_file=config.backup_file):
    cmd = "{0}/backup-postgresql.sh {1} {2}".format(
        config.bash_files,
        container_name,
        backup_file)
    os.system(cmd)

"""
Restore the phpunit db.

@type string
@param container_name Name of the container to restore db.
"""
def restore_phpunit_db(container_name):
    cmd = "{0}/restore-postgresql.sh {1}".format(
        config.bash_files,
        container_name)
    os.system(cmd)

def copy_dir(src_dir, dest_dir):
    os.system("cp -TR {0} {1}".format(src_dir, dest_dir))

def copy_file_to_dir(src_file, dest_dir):
    os.system("cp {0} {1}".format(src_file, dest_dir))

"""
@type *
@param arg The arg to examine.

@type list
@param arg_list The list in which arg belongs.

@type lambda|function
@param handler The handler to the next argument if any.

@type string
@param msg The message to display in error.
"""
def handle_option(option, arg_list, handler, msg="", *args):
    if option in arg_list:
        arg_index = arg_list.index(option) + 1
        try:
            handler(option, arg_list, arg_index, *args)
        except IndexError:
            print msg
            return const.ERROR
        return const.OK
