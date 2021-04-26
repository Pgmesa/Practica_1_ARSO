
from math import floor, ceil
from contextlib import suppress

# --------------------------------------------------------------------        
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
            names_line += ("| " + name.upper() + 
                                " "*(mlength - name_length) + " ")
            values_line += ("| " + " "*dhalf + str(value) + 
                                                    " "*uhalf + " ")
        else:
            dhalf = floor((mlength - name_length)/2)
            uhalf = ceil((mlength - name_length)/2)
            names_line += ("| " +  " "*dhalf + name.upper() +
                                                    " "*uhalf + " ")
            values_line += ("| " + str(value) + 
                                " "*(mlength - value_length) + " ")
    names_line += "|"
    values_line += "|"
    string = (dashes + "\n" + names_line + "\n" + dashes + "\n" +
                                        values_line + "\n" + dashes)
    return string

# --------------------------------------------------------------------
def objectlist_as_dict(l:list, key_attribute:str) -> dict:
    if l == None: return None
    dic = {}
    for obj in l:
        with suppress(Exception):
            dic[getattr(obj, key_attribute)] = obj
    return dic

# --------------------------------------------------------------------   
def concat_array(array, separator=",") -> str:
    c = ""
    for i, obj in enumerate(array):
        if i == len(array) - 1:
            c += str(obj)
        else:
            c += str(obj) + separator + " "
    return c
   
# --------------------------------------------------------------------
def remove_many(*remove, remove_in:list):
    for r in remove:
        with suppress(Exception):
            remove_in.remove(r)

# --------------------------------------------------------------------  