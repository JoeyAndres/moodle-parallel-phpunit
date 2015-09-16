# moodle-parallel-phpunit
Parallel phpunit tool for moodle.

## INTRO:
This is a tool for enabling parallel phpunit for moodle.

## HOW TO USE:

1. git clone https://github.com/JoeyAndres/moodle-parallel-phpunit.git
2. edit config.py
   Set **moodle_directory** to the absolute path of your moodle instance.
   
   Also change *container\_count* to the number of cpu cores that you have.
   
   If it gives you faster result with 2 * core count, then go ahead. I'm
   not recommending it at the moment since it might influence the execution
   time estimates.
   
3. Change the config.php of your moodle instance to the following:

```php
<?php  // Moodle configuration file

unset($CFG);
global $CFG;
$CFG = new stdClass();

$CFG->dbtype    = 'pgsql';
$CFG->dblibrary = 'native';
$CFG->dbhost    = 'localhost';
$CFG->dbname    = 'moodledb';
$CFG->dbuser    = 'moodle';
$CFG->dbpass    = 'moodle';
$CFG->prefix    = 'mdl_';
$CFG->dboptions = array (
  'dbpersist' => 0,
  'dbport' => '',
  'dbsocket' => '',
);

$CFG->wwwroot   = 'http://localhost';
$CFG->dataroot  = '//moodledata';
$CFG->admin     = 'admin';

$CFG->directorypermissions = 0777;

$CFG->phpunit_prefix = 'phpu_';
$CFG->phpunit_dataroot = '/phpu_moodledata';
$CFG->phpunit_dbhost    = '0.0.0.0';

$CFG->behat_prefix = 'b_';
$CFG->behat_dataroot = '//b_moodledata';
$CFG->behat_wwwroot = 'http://127.0.0.1';

require_once(dirname(__FILE__) . '/lib/setup.php');
```

(Currently only handles postgres for Pre-Alpha)

4. Execute _./moodle-parallel-phpunit.py setup  --recreate-image_

   This is semantically wrong, but this is Pre-Alpha so I'm
   not focus on that for now.
   
5. Execute _./moodle-parallel-phpunit.py test_

6. Result should be in data/result.out


## Problems or Question?:
Contact me at jandres@ualberta.ca