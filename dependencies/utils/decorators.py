
import logging
from time import time

# -------------------------------------------------------------------- 
def timer(func):
    def f(*a, **ka):
        root_logger = logging.getLogger()
        t0 = time()
        func(*a,**ka)
        tf = time()
        if root_logger.level <= logging.WARNING:
            print(f"Elapsed time: {round(tf-t0, 2)} s")
    return f

# -------------------------------------------------------------------- 
def catch_foreach(logger=None):
    def _catch_foreach(func):
        def catch (*args, **optionals):
            successful = []
            for a in args:
                try:
                    func(a, **optionals)
                    successful.append(a)
                except Exception as err:
                    if logger == None:
                        print(f"ERROR:{err}")  
                    else:
                        logger.error(err)    
            return successful
        return catch
    return _catch_foreach

# -------------------------------------------------------------------- 