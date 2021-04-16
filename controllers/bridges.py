import logging
import subprocess
from os import remove, path

import register.register as register
from classes.bridge import Bridge, LxcNetworkError

# -----------------------------------------------
root_logger = logging.getLogger()
ctrl_logger = logging.getLogger(__name__)

ID = "bridges"

# def load_bridges() -> list:
#     try:
#         with open("bridges_register", "rb") as file:
#             return load(file)
#     except FileNotFoundError:
#         return None

# def update_bridges_register(bridges:list):
#     with open("bridges_register", "wb") as file:
#         dump(bridges, file)

# def update_bridge(bridge_to_update:Bridge):
#     bridges = load_bridges()
#     index = None
#     for i, b in enumerate(bridges):
#         if b.name == bridge_to_update.name:
#             index = i
#             break
#     if index != None:
#         bridges[index] = bridge_to_update
#         update_bridges_register(bridges)
    
# def load_bridge(name:str) -> Bridge:
#     bridges = load_bridges()
#     for b in bridges:
#         if b.name == name:
#             return b
# -------------------------------------------------

def initBridges(bridges:list) -> dict:
    
    if register.load(register_id=ID) != None:
        ctrl_logger.error(" Los bridges ya han sido creados, " +
                                "se deben destruir los anteriores para crear otros nuevos")
        return None
    
    ctrl_logger.info(" Creando bridges...\n")
    
    successful = {}
    save = []
    for b in bridges:
        try:
            ctrl_logger.info(f" Creando bridge '{b.name}'...")
            b.create()
            ctrl_logger.info(f" bridge '{b.name}' creado con exito")
            save.append(b)
            successful[b.name] = b
        except LxcNetworkError as err:
            ctrl_logger.error(err)
         
    register.add(ID, save)
    
    if root_logger.level <= logging.WARNING:
        subprocess.call(["lxc", "network", "list"])
    return successful

def deleteBridges():
    if register.load(register_id=ID) == None:
        ctrl_logger.error(" No existen bridges creados por el programa")
        return -1
    
    ctrl_logger.info(" Eliminando bridges...\n")
    
    bridges = register.load(register_id=ID)
    
    failures = []
    for b in bridges:
        try:
            ctrl_logger.info(f" Eliminando bridge '{b.name}'...")
            b.delete()
            ctrl_logger.info(f" bridge '{b.name}' eliminado con exito")
        except LxcNetworkError as err:
            failures.append(b)
            ctrl_logger.error(f" Fallo al eliminar bridge '{b.name}' -> {err}")
   
    if len(failures) > 0:
        register.update(ID,failures)
    else:
        register.remove(register_id=ID)
        
    if root_logger.level <= logging.WARNING:
        subprocess.call(["lxc", "network", "list"])

def attach(vm_name:str, to_bridge:Bridge):
    bridge = to_bridge
    ctrl_logger.info(f" Agregando '{vm_name}' al bridge {bridge.name}...")
    try:
        bridge.add_vm(vm_name)
        ctrl_logger.info(f" '{vm_name}' agregado con exito")
    except LxcNetworkError as err:
        ctrl_logger.error(err)
    update_bridge(bridge)
    
def update_bridge(bridge_to_update:Bridge):
    bridges = register.load(register_id=ID)
    index = None
    for i, b in enumerate(bridges):
        if b.name == bridge_to_update.name:
            index = i
            break
    if index != None:
        bridges[index] = bridge_to_update
        register.update(ID, bridges)       
        

