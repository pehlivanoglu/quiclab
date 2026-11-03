"""measure_time from FlowBot src/siamese/preprocess.py, copied verbatim (the
rest of that module needs torch and is not used by the SBD baselines)."""
import time


def measure_time(tag=None):
    """This decorator is used to measure the time of a function.
    tag is given to avoid sometimes the function name is another wrapper.
    """
    def time_decorator(func):
        def time_wrapper(*args, **kwargs):
            start = time.time()
            ftag = tag if tag else func.__name__
            print(f" {start:.3f} s: {ftag} starts ...")
            res = func(*args, **kwargs)
            end = time.time()
            print(f" {end:.3f} s: {ftag} ends, time elapsed: {end - start:.6f} s")
            return res
        return time_wrapper
    return time_decorator
