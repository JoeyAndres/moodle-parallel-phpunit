# phpunit_parallel_test.py

from threading import Thread, Lock

# local imports
from phpunit_container import phpunit_container_abstract
import utility

"""
@class phpunit_parallel_test

Encapsulates the testsuites and containers to be able to form
parallel tests.
"""
class phpunit_parallel_test:

    """
    @type Array of strings
    @param testsuites Test suites to test.
    
    @type phpunit_container_abstract
    @param containers Containers that will SHRED these testsuites.
    """
    def __init__(self, testsuites, containers):
        self.testsuites = testsuites
        self.containers = containers
        self._testsuites_lock = Lock()
        self._thread_array = []
        self.testsuites_time = {}

    """
    Process testsuites one by one.
    
    @chainable
    """
    def run(self):
        for container in self.containers:
            test_routine = lambda: self._run(container)        
            thread_instance = Thread(None,  test_routine)
            self._thread_array.append(thread_instance)
            thread_instance.daemon = True
            thread_instance.start()

        return self

    """
    Call this to block till all tasks are done.
    
    @chainable
    """
    def wait(self):
        for thread in self._thread_array:
            print "Waiting for thread: {0}".format(thread.name)
            thread.join()
        return self

    """
    Feed the container self.testsuites
    
    @type phpunit_container_abstract
    @param container
    """
    def _run(self, container):
        testsuite = self._pop_testsuite()
        while True:
            testsuite = self._pop_testsuite()
            if testsuite is None:
                print 'Done'
                return
            print "{0}: {1}".format(container.container_name, testsuite)
            execution_time = utility.execute_and_time(container.test, testsuite)
            self.testsuites_time[testsuite] = execution_time

    """
    A wrapper of self.testsuite to make it threadsafe.
    
    @return The top of the self.testsuite array.
    """
    def _pop_testsuite(self):
        self._testsuites_lock.acquire(True)        
        testsuite = None
        if len(self.testsuites) > 0:
            testsuite = self.testsuites.pop()
        self._testsuites_lock.release()

        return testsuite
