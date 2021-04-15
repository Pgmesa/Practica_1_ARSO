import logging
import subprocess
from os import remove, path
from pickle import dump, load

from bridges.bridge import Bridge, LxcNetworkError

# -----------------------------------------------
root_logger = logging.getLogger()
ctrl_logger = logging.getLogger(__name__)

def load_bridges() -> list:
    try:
        with open("bridges_register", "rb") as file:
            return load(file)
    except FileNotFoundError:
        return None

def update_bridges_register(bridges:list):
    with open("bridges_register", "wb") as file:
        dump(bridges, file)

def update_bridge(bridge_to_update:Bridge):
    bridges = load_bridges()
    index = None
    for i, b in enumerate(bridges):
        if b.name == bridge_to_update.name:
            index = i
            break
    bridges[index] = bridge_to_update
    update_bridges_register(bridges)
    
def load_bridge(name:str) -> Bridge:
    bridges = load_bridges()
    for b in bridges:
        if b.name == name:
            return b
# -------------------------------------------------

def initBridges(bridges:list):
    if path.isfile("bridges_register"):
        ctrl_logger.error(" Los bridges ya han sido creados, " +
                                "se deben destruir los anteriores para crear otros nuevos")
        return -1
    ctrl_logger.info(" Creando bridges...\n")
    
    successful = []
    for b in bridges:
        try:
            ctrl_logger.info(f" Creando bridge '{b.name}'...")
            b.create()
            ctrl_logger.info(f" bridge '{b.name}' creado con exito")
            successful.append(b)
        except LxcNetworkError as err:
            ctrl_logger.error(err)
         
    update_bridges_register(successful)
    
    if root_logger.level <= logging.WARNING:
        subprocess.call(["lxc", "network", "list"])

def deleteBridges():
    if not path.isfile("bridges_register"):
        ctrl_logger.error(" No existen bridges creados por el programa")
        return -1
    
    ctrl_logger.info(" Eliminando bridges...\n")
    
    bridges = load_bridges()
    
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
        update_bridges_register(failures)
    else:
        remove("bridges_register")
        
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
    
        
        

