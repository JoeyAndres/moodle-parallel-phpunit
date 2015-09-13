# setup.py

import os
import time
import sys

def setup(args):
    # TODO: Encapsulates these in a module and return, don't exit. Let the call deal with the return.
    if len(args) is 0:
        print "No arguments to command given. For more info execute: \"eclass-parallel-phpunit setup --help\"."
        sys.exit(1)
        
    if '--help' in args:
        print "\"eclass-parallel-phpunit setup\" requires the number of parallel phpunit instance to execute. The ideal number is the number of cores in your system. For instance in an 8-core machine: \"eclass-parallel-phpunit setup 8\""

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

    sys.exit(0)
    
    # All is well and good, do some docker stuff.
    
    # 1. Create image if not yet created.
    # TODO: Make image/container name.
    print "Creating eclass-parallel-phpunit image"
    create_docker_img_cmd = "sudo docker build -t eclass-parallel-phpunit ."
    os.system(create_docker_img_cmd)
    
    # 2. Create phpunit_instance_count container based off the image just created.
    # 3. Execute /eclass-unified/vendor/bin/phpunit for each container, to initialize the db.
    for instance_number in range(phpunit_instance_count):
        container = "{0}-{1}".format("eclass-parallel-phpunit", instance_number)
        remove_docker_contaienr_if_exist = "sudo ./remove-container.sh {0} {1}".format(
            container,
            "eclass-parallel-phpunit")
        create_docker_container_cmd = "sudo ./create-eclass-parallel-phpunit-container.sh {0} {1} {2}".format(
            "eclass-parallel-phpunit",
            container,
            "/home/jandres/CompScie/eclass-unified-docker")
        init_docker_container_db_cmd = "sudo ./initialize-eclass-parallel-phpunit-db.sh {0}".format(container)

        print "Removing eclass-parallel-phpunit-{0} container if exist".format(instance_number)
        os.system(remove_docker_contaienr_if_exist)

        print "Creating eclass-parallel-phpunit-{0} container".format(instance_number)
        os.system(create_docker_container_cmd)
        
        os.system("sudo ./check-pgsql-status.sh {0}".format(container))

        print "Initializing eclass-parallel-phpunit-{0} phpunit db".format(instance_number)
        os.system(init_docker_container_db_cmd)
