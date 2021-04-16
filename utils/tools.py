import logging
import traceback
from time import time
from math import floor, ceil
from functools import reduce

from controllers import vms, bridges
import register.register as register

        
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

    
    
    