# phpunit_parallel_test.py

from threading import Thread, Lock
import operator

# local imports
from phpunit_container import phpunit_container_abstract
import utility
import config
import const


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

    @type dict
    @param old_testsuites_time Old dictionary testsuites => execution time(s)
    """
    def __init__(self, testsuites, containers, old_testsuites_times):
        self.testsuites = testsuites
        self.testsuites_count = len(self.testsuites)
        self.containers = containers
        self.testsuites_time = {}

        # @type dict
        # @var passed A dictionary of container name and its corresponding result.
        # TODO: Make container hashable based on its name.
        self.passed = {}
        for container in self.containers:
            self.passed[container.name]=True 
        
        self._testsuites_lock = Lock()
        self._thread_array = []
        self._old_testsuites_times = old_testsuites_times

        # See if there are new/discarded testsuites since last time.
        # If so update old_testsuites.
        new_testsuites = []
        for testsuite in self.testsuites:
            testsuite_new = self._old_testsuites_times.has_key(testsuite) is False
            if testsuite_new:
                self._old_testsuites_times[testsuite] = 666
                new_testsuites.append(testsuite)

        discarded_testsuites = []
        for testsuite in self._old_testsuites_times.keys():
            testsuite_discarded = testsuite not in self.testsuites
            if testsuite_discarded:
                discarded_testsuites.append(testsuite)
                del self._old_testsuites_times[testsuite]

        # Now that old testsuites is updated (contains same keys as testsuites),
        # let is sort it based on execution time decreasing, and set
        # the testsuites. This should give us the optimal time.
        sorted_testsuites_time = sorted(self._old_testsuites_times.items(),
                                        key=operator.itemgetter(1),
                                        reverse=False)
        self.testsuites = [testsuite[0] for testsuite in sorted_testsuites_time]

        # Reports.
        print "New testsuites: "
        print new_testsuites
        print "\n"
        
        print "Discared testsuites: "
        print discarded_testsuites
        print "\n"

        print "Test Suites (Sorted in ascending order in execution time): "
        print self.testsuites
        print "\n"
            
    """
    Creates thread for each container.
    
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

    @return const.TEST_PASSED if no error. Otherwise const.TEST_FAILED.
    """
    def _run(self, container):
        return_value = const.TEST_PASSED
        while True:
            testsuite = self._pop_testsuite()
            if testsuite is None:
                print 'Done'
                return
            
            (execution_time, passed) = utility.execute_and_time_with_return(
                container.test, testsuite)
            result = "PASSED" if passed else "FAILED"
            print "{0}: {1} {2}/{3}. {4}".format(container.name,
                                                 testsuite,
                                                 self.testsuites_count - len(self.testsuites),
                                                 self.testsuites_count,
                                                 result)
            self.testsuites_time[testsuite] = execution_time

            # If passed is false end this test.
            # TODO: Make this overridable in a terminal argument.
            if passed is False:
                return_value = const.TEST_FAILED
                # return const.TEST_FAILED

        passed = True if return_value is const.TEST_PASSED else False
        self.passed[container.name] = passed
        
        return return_value

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
