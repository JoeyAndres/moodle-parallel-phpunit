# utility.py

import time

"""
@type function|lambda
@param fn_or_lambda function or lambda to be executed and timed.

@type *args
@param *args Python's *args, (aka varargs). Dereferences a tuple if only args.

@return integer (s)
"""
def execute_and_time(fn_or_lambda, *args):
    start_time = time.time()
    fn_or_lambda(*args)
    end_time = time.time()
    return end_time - start_time
