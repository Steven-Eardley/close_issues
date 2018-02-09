import time
from functools import wraps
""" Rate limit a function call, from DOAJ / GitHub issue closer """


def rate_limited(freq=float('inf')):
    """
    Apply a rate limit to a function
    :param freq: rate limit to be applied in Hertz (number per second)

    Example usage:
    @rate_limited(0.5)
    def my_func():
        #do something

    Would allow my_func() to run at 0.5 Hertz, or twice per second.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            global rl_last_run
            try:
                diff = time.time() - rl_last_run
            except NameError:
                diff = float('inf')         # Never run, so infinite diff
            if diff < 1.0 / float(freq):
                time.sleep(1.0 / freq - diff)
            rl_last_run = time.time()
            return fn(*args, **kwargs)
        return wrapper
    return decorator
