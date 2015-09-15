# setup.py

import os
import time
import sys
import subprocess

import phpunit_container


"""
"""
def _recreate_image():
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
        print "No arguments to command given. For more info execute: \"eclass-parallel-phpunit setup --help\"."
        sys.exit(1)
        
    if '--help' in args:
        print "\"eclass-parallel-phpunit setup\" requires the number of parallel phpunit instance to execute. The ideal number is the number of cores in your system. For instance in an 8-core machine: \"eclass-parallel-phpunit setup 8\""

    if '--recreate-image' in args:
        _recreate_image()

    phpunit_instance_count = None
    try:
        phpunit_instance_count = int(args[0])
    except ValueError:
        print "Argument {0} given is not a positive integer. For more info execute: \"eclass-parallel-phpunit setup --help\".".format(args[0])
        sys.exit(1)

    # Save some data for other commands.
    config_str = '''
    container-count: {0}
    '''.strip().format(phpunit_instance_count)

    print config_str
    
    config_file = open(".config", 'w')
    config_file.write(config_str)
    
    # All is well and good, do some docker stuff. 
    os.system("mkdir -p phpu_moodledata-0")
    
    instance_number = 0
    container = "{0}-{1}".format("eclass-parallel-phpunit", instance_number)
    remove_docker_contaienr_if_exist = "./remove-container.sh {0}".format(container)
    create_docker_container_cmd = "./create-eclass-parallel-phpunit-container.sh {0} {1} {2} {3}".format(
        "eclass-parallel-phpunit-first",
        container,
        "/home/jandres/CompScie/eclass-unified-docker,"
        "\"-v /home/jandres/CompScie/docker/docker-eclass-phpunit/phpu_moodledatas/phpu_moodledata-0:/phpu_moodledata \"")
    init_docker_container_db_cmd = "./initialize-eclass-parallel-phpunit-db.sh {0}".format(container)
    backup_docker_container_db_cmd = "./backup-postgresql.sh {0} {1}".format(container, container)

    print "Removing eclass-parallel-phpunit-{0} container if exist".format(instance_number)
    os.system(remove_docker_contaienr_if_exist)

    print "Creating eclass-parallel-phpunit-{0} container".format(instance_number)
    os.system(create_docker_container_cmd)

    os.system("./check-pgsql-status.sh {0}".format(container))

    print "Initializing eclass-parallel-phpunit-{0} phpunit db".format(instance_number)
    os.system(init_docker_container_db_cmd)

    print "Backing up eclass-parallel-phpunit-{0} phpunit db".format(instance_number)
    os.system(backup_docker_container_db_cmd)
    
    # 2. Create phpunit_instance_count container based off the image just created.
    # 3. Execute /eclass-unified/vendor/bin/phpunit for each container, to initialize the db.
    for instance_number in range(1, phpunit_instance_count):
        container = "{0}-{1}".format("eclass-parallel-phpunit", instance_number)
        remove_docker_contaienr_if_exist = "./remove-container.sh {0}".format(container)
        create_docker_container_cmd = "./create-eclass-parallel-phpunit-container.sh {0} {1} {2} {3}".format(
            "eclass-parallel-phpunit",
            container,
            "/home/jandres/CompScie/eclass-unified-docker",
            " \"-v /home/jandres/CompScie/docker/docker-eclass-phpunit/phpu_moodledatas/phpu_moodledata-{0}:/phpu_moodledata\" ".format(instance_number))
        restore_docker_container_db_cmd = "./restore-postgresql.sh {0}".format(container)
        
        os.system("cp -TR /home/jandres/CompScie/docker/docker-eclass-phpunit/phpu_moodledatas/phpu_moodledata-0 /home/jandres/CompScie/docker/docker-eclass-phpunit/phpu_moodledatas/phpu_moodledata-{0}".format(instance_number))
        os.system("cp /home/jandres/CompScie/docker/docker-eclass-phpunit/phpu_moodledb.sql /home/jandres/CompScie/docker/docker-eclass-phpunit/phpu_moodledatas/phpu_moodledata-{0}/".format(instance_number))

        print "Removing eclass-parallel-phpunit-{0} container if exist".format(instance_number)
        os.system(remove_docker_contaienr_if_exist)

        print "Creating eclass-parallel-phpunit-{0} container".format(instance_number)
        os.system(create_docker_container_cmd)
        
        os.system("./check-pgsql-status.sh {0}".format(container))

        print "Restoring eclass-parallel-phpunit-{0} phpunit db from eclass-parallel-phpunit-0".format(instance_number)
        os.system(restore_docker_container_db_cmd)
