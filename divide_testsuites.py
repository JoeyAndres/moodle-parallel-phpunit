"""
phpunit-divide-testsuites.py

Extracts the testsuites from phpunit.xml and divides it n ways.
"""

import xml.etree.ElementTree as ET

def divide_testsuites(phpunit_xml_dir, n_divide):

    phpunit_xml_tree = ET.parse(phpunit_xml_dir)
    phpunit_xml_root = phpunit_xml_tree.getroot()

    testsuites_node = phpunit_xml_root[1];

    # Acquire all the testsuites and placed them in testsuites_arr.
    testsuites_arr=[]
    for testsuite_node in testsuites_node:
        # See if testsuite node have any child nodes (aka directory nodes).
        if len(testsuite_node) > 0:
            testsuites_arr.append(testsuite_node.get('name'))

    # Divide the testsuites_arr as evenly as possible.
    testsuites_count = len(testsuites_arr)
    divided_testsuites_count = testsuites_count/n_divide  # Should be an integer.
    remainder_testsuites_count = testsuites_count % n_divide  # Let's not forget about the left overs like in morefontcolors.

    divided_testsuites_group = []

    docker_instance_counter=0
    eclass_dir="/home/jandres/CompScie/eclass-unified-docker"
    while len(testsuites_arr):
        divided_testsuites_group.append(testsuites_arr[:divided_testsuites_count])
        testsuites_arr = testsuites_arr[divided_testsuites_count:]  # Get rid of the first divided_testsuites_count

    return divided_testsuites_group
