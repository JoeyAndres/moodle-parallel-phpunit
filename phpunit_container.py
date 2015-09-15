# phpunit_container.py

import os


"""
@class phpunit_container_abstract

Base class for phpunit containers.
"""
class phpunit_container_abstract(object):
    
    """
    @type container_image_name string
    @param container_image_name Name of the docker image in which this container
                                is based upon.

    @type container_name string
    @param container_name Name of the docker container.

    @type enable_logging Boolean
    @param enable_logging Set to True to enable logging.
    """
    def __init__(self, container_image_name, container_name, enable_logging):
        self.container_image_name = container_image_name
        self.container_name = container_name
        self.logging_enable = enable_logging
        
    """
    Removes the container if it exist. Call this prior to self.create
    """
    def remove_if_exist(self):
        if self.logging_enable:
            print "Removing {0} container if exist".format(self.container_name)
            
        cmd = "./remove-container.sh {0}".format(self.container_name)
        os.system(cmd)

    """
    Creates the container.
    """
    def create(self):
        if self.logging_enable:
            print "Creating {0} container".format(self.container_name)

        cmd = "./create-eclass-parallel-phpunit-container.sh {0} {1} {2} {3}".format(
            self.container_image_name,
            self.container_name,
            "/home/jandres/CompScie/eclass-unified-docker",  # todo: Make this part of the constructor.
            "\"-v /home/jandres/CompScie/docker/docker-eclass-phpunit/phpu_moodledatas/{0}:/phpu_moodledata \"".format(self.container_name))
        os.system(cmd)

    """
    Initialize the phpunit database and phpu_moodledata.
    """
    def init_phpunit_db(self):
        os.system("./check-pgsql-status.sh {0}".format(self.container_name))

    """
    @type string
    @param testsuite to execute
    """
    def test(self, testsuite):
        cmd = "./test-eclass-parallel-phpunit.sh {0} \"{1}\"".format(
            self.container_name,
            testsuite)
        os.system(cmd)

    """
    @type array of string
    @param testsuites to execute
    """
    def tests(self, testsuites):
        test_cmd = "./test-eclass-parallel-phpunit.sh {0} \"{1}\"".format(
            self.container_name, " ".join(testsuites))
        os.system(test_cmd)


"""
@class phpunit_container_master

The phpunit in which the slaves are based upon. This is introduced for performance reasons.
Since "php admin/tool/phpunit/cli/init.php" is simply too slow, the following is done instead:

1. pg_dump -Fc > backup.sql (master)
2. pg_restore -j 16 -f backup.sql (slave)
3. Copy phpu_moodledata from master to slave.

Personal benchmark 8-core 2.7ghz cpu and SSD:
-php admin/tool/phpunit/cli/init.php: 139.546 s
-"backup and restore" method: 39 s.

Though, not linear, still significant. About 3.5x faster than otherwise !!!
"""
class phpunit_container_master(phpunit_container_abstract):

    def __init__(self, container_image_name, container_name, enable_logging):
        super(phpunit_container_master, self).__init__(container_image_name,
                                                       container_name,
                                                       enable_logging)

    def create(self):
        """
        Create the appropriate phpu_moodledata directory. This will be a volume
        in docker container, and will then be copied to the slaves to avoid
        duplication.
        """
        os.system("mkdir -p ./phpu_moodledatas/{0}".format(self.container_name))
        super(phpunit_container_master, self).create()

    def init_phpunit_db(self):
        """
        Call the usual initialization of phpunit database. Then backup the created
        phpunit database. This backup file, will be used to populate 
        slave phpunit dbs.
        """
        
        super(phpunit_container_master, self).init_phpunit_db()
        
        if self.logging_enable:
            print "Initializing {0} phpunit db".format(self.container_name)
            
        init_cmd = "./initialize-eclass-parallel-phpunit-db.sh {0}".format(self.container_name)
        os.system(init_cmd)

        if self.logging_enable:
            print "Backing up {0} phpunit db".format(self.container_name)
            
        backup_cmd = "./backup-postgresql.sh {0} {1}".format(self.container_name, 'phpu_moodledb.sql')
        os.system(backup_cmd)


"""
@class phpunit_container_slave

Containers that are dependent on a @see phpunit_container_master
"""
class phpunit_container_slave(phpunit_container_abstract):

    """
    @type container_image_name string
    @param container_image_name

    @type container_name string
    @param container_name

    @type phpunit_container_master @see phpunit_container_master
    @param master_container The master container.

    @type enable_logging Boolean
    @param enable_logging
    """
    def __init__(self, container_image_name, container_name, master_container, enable_logging):
        super(phpunit_container_slave, self).__init__(container_image_name,
                                                      container_name,
                                                      enable_logging)
        self.master_container = master_container

    def create(self):
        """
        To avoid duplicate creation of phpunit's moodledata, this is copied from
        self.master_container.
        """
        
        # TODO: Based this all off the master_container
        os.system("cp -TR /home/jandres/CompScie/docker/docker-eclass-phpunit/phpu_moodledatas/{0} /home/jandres/CompScie/docker/docker-eclass-phpunit/phpu_moodledatas/{1}".format(
            self.master_container.container_name,
            self.container_name))
        os.system("cp /home/jandres/CompScie/docker/docker-eclass-phpunit/phpu_moodledb.sql /home/jandres/CompScie/docker/docker-eclass-phpunit/phpu_moodledatas/{0}/".format(self.container_name))

        super(phpunit_container_slave, self).create()
        

    def init_phpunit_db(self):
        """
        For fast initialization, self.create copies phpu_moodledata of 
        self.master_container and restore backup file of
        self.master_container.
        """
        
        super(phpunit_container_slave, self).init_phpunit_db()
        
        if self.logging_enable:
            print "Restoring {0} phpunit db from {1}".format(self.container_name, self.master_container.container_name)

        cmd = "./restore-postgresql.sh {0}".format(self.container_name)
        os.system(cmd)
