#!/usr/bin/env python

import sys
import xml.etree.ElementTree as ET
import os.path
from sets import Set
# import subprocess
import os

# Local file.
import setup
import destroy
import test

options = {
    'setup': setup.setup,
    'destroy': destroy.destroy,
    'test': test.test
}

cmd = sys.argv[1]  # phpunit xml location.

if options.has_key(cmd) is False:
    print "Error: Unknown command. Enter one of the following commands {0}.".format(options.keys())
    sys.exit(1)

# Execute command with the rest of the arguments. These submodules should handle the validity
# of arguments and print appropriate error messages if possible.
options[cmd](sys.argv[2:])
