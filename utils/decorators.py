
import logging
from time import time

def timer(func):
    def f(*a, **ka):
        root_logger = logging.getLogger()
        t0 = time()
        func(*a,**ka)
        tf = time()
        if root_logger.level <= logging.WARNING:
            print(f"Elapsed time: {round(tf-t0, 2)} s")
    return f