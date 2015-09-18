# phpunit_parallel_test.py

from threading import Thread, Lock
import operator

# local imports
import utility
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
        self.passed = dict([(c, True) for c in self.containers])

        # Keeps track of he failed testsuites.
        self.failed_testsuites = []

        # @type Lock
        # @var _testsuites_lock Mutex for self.testsuites. This avoids data race
        #                             when containers acquire testsuites to test.
        self._testsuites_lock = Lock()

        # @type array
        # @var _thread_array Keeps reference of threads that feeds the container
        #                     testsuites. (Note: container are already running,
        #                     and we are not controlling their thread. That's
        #                     Docker's job).
        self._thread_array = []

        # @type dict
        # @var _old_testsuites_times A mapping of testsuites to execution time
        #                            from last run (ideally successful run).
        #                            This will help us achieve optimal execution
        #                            time.
        self._old_testsuites_times = old_testsuites_times

        # @type boolean
        # @var stop_on_failure set to True to stop immediately in failure.
        self.stop_on_failure = False

        # @type boolean
        # @var _stop_flag Set to true when one of the unittest fail and
        #                self.stop_on_failure is set to true. This allows
        #                containers to finnish what they were doing, allowing
        #                a safe exit, instead of the kill alternative.
        self._stop_flag = False

        discarded_testsuites, new_testsuites = \
            self._sync_testsuites_and_old_testsuites_times()

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
            thread_instance = Thread(None, lambda: self._run(container))
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
        while self._stop_flag is False:
            testsuite = self._pop_testsuite()
            if testsuite is None:
                print container.name, " can't crunch anymore testsuites."
                break
            
            (execution_time, passed) = \
                utility.execute_and_time_with_return(container.test, testsuite)
            result_msg = "PASSED" if passed else "FAILED"
            self._prompt_testsuite_result(container, result_msg, testsuite)
            self.testsuites_time[testsuite] = execution_time

            # If passed is false end this test.
            if passed is False:
                self.failed_testsuites.append(testsuite)
                return_value = const.TEST_FAILED

                if self.stop_on_failure:
                    print "Failure occured, waiting for the currently executed " \
                          "testsuites to stop."
                    self._stop_flag = True
                    break

        passed = True if return_value is const.TEST_PASSED else False
        self.passed[container.name] = passed
        
        return return_value

    """
    @type phpunit_container_abstract
    @param container

    @type string
    @param msg Result message.

    @type string
    @param testsuite String of the testsuite being executed.
    """
    def _prompt_testsuite_result(self, container, msg, testsuite):
        testsuites_left = self.testsuites_count - len(self.testsuites)
        print "{0}: {1} {2}/{3}. {4}".format(container.name,
                                             testsuite,
                                             testsuites_left,
                                             self.testsuites_count,
                                             msg)

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

    """
    Sync self.testsuites and self._old_testsuites_times. This is
    because self.testsuites contains the latest testsuites whilst
    self._old_testsuites_times contains a dictionary of the testsuites
    from last run and its corresponding execution time, thus needs to be
    updated.
    """
    def _sync_testsuites_and_old_testsuites_times(self):
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
        return discarded_testsuites, new_testsuites