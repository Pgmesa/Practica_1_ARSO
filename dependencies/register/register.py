
import os
import pickle
from contextlib import suppress

# -------------------------------------------------------------------- 
class RegisterError(Exception):
    def __init__(self, msg):
        super().__init__(msg)

# --------------------------------------------------------------------         
REL_PATH = ".register"
    
def config_location(path, name=".register"):
    global REL_PATH
    REL_PATH = path+name

# --------------------------------------------------------------------    
def add(register_id:any, obj:object):
    if not os.path.exists(REL_PATH):
        register = {}
    else:
        register = load()
    
    if register_id in register:
        raise RegisterError(" id -> '{}' is already used in the register")
    else:
        register[register_id] = obj
        
    with open(REL_PATH, "wb") as file:
            pickle.dump(register, file)

# -------------------------------------------------------------------- 
def update(register_id:any, obj:object, override:bool=True, dict_id:any=None):
    register = load()
    if register == None or register_id not in register:
        err_msg = f" id -> '{register_id}' was not found in the register"
        raise RegisterError(err_msg)
    if override == True:
        register[register_id] = obj
    else:
        value_saved = register[register_id]
        if type(value_saved) == list:
            value_saved.append(obj)
        elif type(value_saved) == set:
            value_saved.add(obj)
        elif type(value_saved) == dict:
            if dict_id != None:
                value_saved[dict_id] = obj
            else:
                err_msg = (
                    " A key is needed ('dict_id' property) for updating " + 
                        "(without overriding) the dictionary saved in the " + 
                            f"register with id '{register_id}'"
                )
                raise RegisterError(err_msg)
        elif type(value_saved) == tuple:
            err_msg = (
                    " A tuple object needs to be override it " + 
                    f"(change 'override' property)"
                )
            raise RegisterError(err_msg)
        else:
            array = [value_saved, obj]
            register[register_id] = array
    with open(REL_PATH, "wb") as file:
        pickle.dump(register, file)   

# --------------------------------------------------------------------     
def load(register_id:any=None) -> object:
    try:
        with open(REL_PATH, "rb") as file:
            register = pickle.load(file)
        if register_id == None:
            return register
        else:
            if register_id in register:
                return register[register_id]
            else:
                return None
    except FileNotFoundError:
        return None

# -------------------------------------------------------------------- 
def override(register):
    with open(REL_PATH, "wb") as file:
        pickle.dump(register, file)

# --------------------------------------------------------------------    
def remove(register_id=None):
    if register_id != None:
        register = load()
        if register_id in register:
            register.pop(register_id)
            if len(register) == 0:
                os.remove(REL_PATH)
            else:
                override(register)
        else:
            raise RegisterError(f" id '{register_id}' was not found")
    else:
        if os.path.exists(REL_PATH): 
            os.remove(REL_PATH)

# -------------------------------------------------------------------- 

