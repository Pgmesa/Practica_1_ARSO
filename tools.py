import logging
import traceback
from time import time
from math import floor, ceil
from functools import reduce

from controllers import vms, bridges
import register.register as register

root_logger = logging.getLogger()

def timer(func):
    def f(*a, **ka):
        t0 = time()
        func(*a,**ka)
        tf = time()
        if root_logger.level <= logging.WARNING:
            print(f"Elapsed time: {round(tf-t0, 2)} s")
    return f

def printProgramState():
    _vms = register.load(register_id=vms.ID)
    _bridges = register.load(register_id=bridges.ID)
    print("VIRTUAL MACHINES")
    if _vms != None:
        for vm in _vms:
            print(pretty(vm))
    else:
        print("No virtual machines created by the program")
    print("BRIDGES")
    if _bridges != None:       
        for b in _bridges:
            print(pretty(b))
    else:
        print("No bridges created by the program")
        
def pretty(obj:object) -> str:
    dashes = ""
    names_line = ""
    values_line = ""
    
    prop = vars(obj)
    names = prop.keys()
    values = prop.values()
    max_lengths = []
    for name, val in zip(names, values):
        m = max(len(name), len(str(val)))
        dashes += "-"*(3 + m)
        max_lengths.append(m)
    dashes += "-"
    for name, value, mlength in zip(names, values, max_lengths):
        name_length = len(name)
        value_length = len(str(value))
        if name_length == mlength:
            dhalf = floor((mlength - value_length)/2)
            uhalf = ceil((mlength - value_length)/2)
            names_line += "| " + name.upper() + " "*(mlength - name_length) + " "
            values_line += "| " + " "*dhalf + str(value) + " "*uhalf + " "
        else:
            dhalf = floor((mlength - name_length)/2)
            uhalf = ceil((mlength - name_length)/2)
            names_line += "| " +  " "*dhalf + name.upper() + " "*uhalf + " "
            values_line += "| " + str(value) + " "*(mlength - value_length) + " "
    names_line += "|"
    values_line += "|"
    string = dashes + "\n" + names_line + "\n" + dashes + "\n" + values_line + "\n" + dashes
    return string

    
    
    