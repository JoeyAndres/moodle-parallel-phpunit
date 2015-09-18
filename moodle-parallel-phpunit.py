#!/usr/bin/env python

import sys
import time

# Local file.
import setup
import destroy
import test
import const

def help():
    print """
    {0} [COMMAND] [OPTIONS]
    
    COMMANDS:
    * setup: Sets up the phpunit db.
    * test: Executes the tests..
    * destroy: Destroys all the container/phpunit instances. (WIP)

    For more information for each command use:
    {0} [COMMAND] --help
    """.format(const.APP_NAME)

options = {
    'setup': setup.setup,
    'destroy': destroy.destroy,
    'test': test.test,
    '--help': help
}

no_arg = sys.argv[1] is None

if no_arg:
    print """
    Error: No arguments. Execute: {0} --help for a list of commands.
    """.format(const.APP_NAME)

cmd = sys.argv[1]  # phpunit xml location.

if options.has_key(cmd) is False:
    print "Error: Unknown command. Enter one of the following commands {0}.".format(options.keys())
    sys.exit(1)

# Execute command with the rest of the arguments. These submodules should handle the validity
# of arguments and print appropriate error messages if possible.
start_time = time.time()
result = options[cmd](sys.argv[2:])
end_time = time.time()

print("--- Total: {0}s seconds ---".format(end_time - start_time))

exit_status = 0 if result is const.OK else 1
sys.exit(exit_status)
