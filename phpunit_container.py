# phpunit_container.py

import os

# Local
import config
import utility


"""
@class phpunit_container_abstract

Base class for phpunit containers.
"""
class phpunit_container_abstract(object):
    
    """
    @type string
    @param image_name Name of the docker image in which this container
                                is based upon.

    @type string
    @param container_name Name of the docker container.

    @type string
    @param result_file File path to the result file.

    @type Boolean
    @param enable_logging Set to True to enable logging.
    """
    def __init__(self, image_name, name, result_file, enable_logging):
        self.image_name = image_name
        self.name = name
        self.result_file = result_file
        self.logging_enable = enable_logging
    
    """
    Removes the container if it exist. Call this prior to self.create
    """
    def remove_if_exist(self):
        if self.logging_enable:
            print "Removing {0} container if exist".format(self.name)
        utility.remove_container(self.name)

    """
    Starts the container.

    @throw SystemError when container don't exist.
    """
    def start(self):
        if self.logging_enable:
            print "Starting {0} container".format(self.name)
        utility.start_container(self.name)

    """
    Creates the container.
    """
    def create(self):
        if self.logging_enable:
            print "Creating {0} container".format(self.name)

        utility.create_container(self.image_name, self.name)

    """
    Initialize the phpunit database and phpu_moodledata.
    """
    def init_phpunit_db(self):
        utility.block_while_initializing_db(self.name)

    """
    Run a test on a testsuite and append it in the result file.

    @type string
    @param testsuite to execute
    """
    def test(self, testsuite):
        utility.run_phpunit_test(self.name, [testsuite], self.result_file)

    """
    Run a test on an array of testsuite and append it in the result file.

    @type array of string
    @param testsuites to execute
    """
    def tests(self, testsuites):
        utility.run_phpunit_test(self.name, testsuites, self.result_file)


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

    def __init__(self, image_name, name, result_file, enable_logging):
        super(phpunit_container_master, self).__init__(image_name,
                                                       name,
                                                       result_file,
                                                       enable_logging)

    def create(self):
        """
        Create the appropriate phpu_moodledata directory. This will be a volume
        in docker container, and will then be copied to the slaves to avoid
        duplication.
        """
        os.system("mkdir -p {0}/{1}".format(config.temp_directory,
                                            self.name))
        super(phpunit_container_master, self).create()

    def init_phpunit_db(self):
        """
        Call the usual initialization of phpunit database. Then backup the created
        phpunit database. This backup file, will be used to populate 
        slave phpunit dbs.
        """
        
        super(phpunit_container_master, self).init_phpunit_db()
        
        if self.logging_enable:
            print "Initializing {0} phpunit db".format(self.name)
        utility.initialize_phpunit_db(self.name)

        if self.logging_enable:
            print "Backing up {0} phpunit db".format(self.name)
        utility.backup_phpunit_db(self.name)
        

"""
@class phpunit_container_slave

Containers that are dependent on a @see phpunit_container_master
"""
class phpunit_container_slave(phpunit_container_abstract):

    def __init__(self, image_name, name, master_container, result_file, enable_logging):
        super(phpunit_container_slave, self).__init__(image_name,
                                                      name,
                                                      result_file,
                                                      enable_logging)
        self.master_container = master_container

    def create(self):
        """
        To avoid duplicate creation of phpunit's moodledata, this is copied from
        self.master_container.
        """
        
        src_dir = "{0}".format(
            config.container_phpunit_dir_template.format(self.master_container.name))
        dest_dir = "{0}".format(config.container_phpunit_dir_template.format(self.name))
        utility.copy_dir(src_dir, dest_dir)
        utility.copy_file_to_dir(config.backup_file, dest_dir)

        super(phpunit_container_slave, self).create()
        

    def init_phpunit_db(self):
        """
        For fast initialization, self.create copies phpu_moodledata of 
        self.master_container and restore backup file of
        self.master_container.
        """
        
        super(phpunit_container_slave, self).init_phpunit_db()
        
        if self.logging_enable:
            print "Restoring {0} phpunit db from {1}".format(self.name, self.master_container.name)
        utility.restore_phpunit_db(self.name)
