#!/usr/bin/env python

import sys
import time
# import subprocess
import os

# Local file.
import setup
import destroy
import test

def help():
    print """
    eclass-parallel-phpunit [COMMAND] [OPTIONS]
    
    COMMANDS:
    * setup: Sets up the container/phpunit instances.
    * test: Divides and executes the tests.
    * destroy: Destroys all the container/phpunit instances.

    For more information for each command use:
    eclass-parallel-phpunit [COMMAND] --help
    """

options = {
    'setup': setup.setup,
    'destroy': destroy.destroy,
    'test': test.test,
    '--help': help
}

no_arg = sys.argv[1] is None;

if no_arg:
    print "Error: No arguments. Execute: eclass-parallel-phpunit --help for a list of commands."

cmd = sys.argv[1]  # phpunit xml location.

if options.has_key(cmd) is False:
    print "Error: Unknown command. Enter one of the following commands {0}.".format(options.keys())
    sys.exit(1)

# Execute command with the rest of the arguments. These submodules should handle the validity
# of arguments and print appropriate error messages if possible.
start_time = time.time()
options[cmd](sys.argv[2:])
end_time = time.time()

print("--- Total: {0}s seconds ---".format(end_time - start_time))
