# phpunit_container.py

import os


"""
"""
class phpunit_container_abstract:
    instance_counter = 0  # TODO: Make a factory method that handles this.
    
    """
    @param container_image_name
    @param base_container_name
    @param enable_logging
    """
    def __init__(self, container_image_name, base_container_name, enable_logging):
        self.logging_enable = enable_logging
        
        self.instance_number = instance_counter
        instance_counter += 1
        print instance_counter

        self.container_name = base_container_name + '-' + self.instance_number
        self.container_image_name = container_image_name

    """
    """
    def remove_if_exist(self):
        if self.logging_enable:
            print "Removing {0} container if exist".format(self.container_name)
            
        cmd = "./remove-container.sh {0}".format(self.container_name)
        os.system(cmd)

    """
    """
    def create_container(self):
        if self.logging_enable:
            print "Creating {0} container".format(self.container_name)

        cmd = "./create-eclass-parallel-phpunit-container.sh {0} {1} {2} {3}".format(
            self.container_image_name, self.container_name,
            "/home/jandres/CompScie/eclass-unified-docker,"  # todo: Make this part of the constructor.
            "\"-v /home/jandres/CompScie/docker/docker-eclass-phpunit/phpu_moodledatas/{0}:/phpu_moodledata \"".format(self.container_name))
        os.system(cmd)

    """
    """
    def init_phpunit_db(self):
        os.system("./check-pgsql-status.sh {0}".format(container))


"""
@class phpunit_container_master

The phpunit in which the slaves are based upon. This is introduced for performance reasons.
Since "php admin/tool/phpunit/cli/init.php" is simply too slow, the following is done instead:

1. pg_dump -Fc > backup.sql (master)
2. pg_restore -j 16 -f backup.sql (slave)
3. Copy phpu_moodledata from master to slave.

Which is (hopefully) faster.
"""
class phpunit_container_master(phpunit_container_abstract):

    """
    @type container_image_name string
    @param container_image_name

    @type base_container_name string
    @param base_container_name

    @type enable_logging Boolean
    @param enable_logging
    """
    def __init__(self, container_image_name, base_container_name, enable_logging):
        super.__init__(self, container_image_name, base_container_name, enable_logging)

    """
    """
    def create_container(self):
        os.system("mkdir -p {0}".format(container_image_name))
        super.create_container(self)

    """
    """
    def init_phpunit_db(self):
        super.init_phpunit_db(self)
        
        if self.logging_enabled:
            print "Initializing {0} phpunit db".format(self.container_name)
            
        init_cmd = "./initialize-eclass-parallel-phpunit-db.sh {0}".format(self.container_name)
        os.system(init_cmd)

        if self.logging_enabled:
            print "Backing up {0} phpunit db".format(self.container_name)
            
        backup_cmd = "./backup-postgresql.sh {0} {1}".format(self.container_name, self.container_name)
        os.system(backup_cmd)


"""
@class phpunit_container_slave

Containers that are dependent on a @see phpunit_container_master
"""
class phpunit_container_slave(phpunit_container_abstract):
    
    """
    @type container_image_name string
    @param container_image_name

    @type base_container_name string
    @param base_container_name

    @type master_container phpunit_container_master
    @param master_container 

    @type enable_logging Boolean
    @param enable_logging
    """
    def __init__(self, container_image_name, base_container_name, master_container, enable_logging):
        super.__init__(self, container_image_name, base_container_name, enable_logging)
        
        self.master_container = master_container

    def create_container(self):
        super.init_phpunit_db(self)
        
        # TODO: Based this all off the master_container
        os.system("cp -TR /home/jandres/CompScie/docker/docker-eclass-phpunit/phpu_moodledatas/phpu_moodledata-0 /home/jandres/CompScie/docker/docker-eclass-phpunit/phpu_moodledatas/{0}".format(self.container_name))
        os.system("cp /home/jandres/CompScie/docker/docker-eclass-phpunit/phpu_moodledb.sql /home/jandres/CompScie/docker/docker-eclass-phpunit/phpu_moodledatas/{0}/".format(self.container_name))

        super.create_container(self)

    def init_phpunit_db(self):
        super.init_phpunit_db(self)
        
        if self.enabled_logging:
            print "Restoring {0} phpunit db from {1}".format(self.container_name, self.master_container.container_name)

        cmd = "./restore-postgresql.sh {0}".format(self.container_name)
        os.system(cmd)
