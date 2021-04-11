from bridges.bridge import Bridge, LxcNetworkError
from vms.vm import VirtualMachine
from pickle import dump, load
from os import remove, path
import logging
import subprocess

logging.basicConfig(level=logging.NOTSET)
ctrl_logger = logging.getLogger(__name__)

# -----------------------------------------------
def load_bridges() -> list:
    with open("bridges_register", "rb") as file:
        bridges = load(file)
    return bridges

def update_bridges_register(bridges):
    with open("bridges_register", "wb") as file:
        dump(bridges, file)

def update_bridge(bridge_to_update):
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
        ctrl_logger.warning(" Los bridges ya han sido creados, " +
                                "se deben destruir los anteriores para crear otros nuevos")
        return
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
    
    if ctrl_logger.level <= logging.INFO:
        subprocess.call(["lxc", "network", "list"])

def deleteBridges():
    if not path.isfile("bridges_register"):
        ctrl_logger.warning(" No existen bridges creadas por el programa")
        return
    
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
        
    if ctrl_logger.level <= logging.INFO:
        subprocess.call(["lxc", "network", "list"])

def attach(vm:VirtualMachine, to_bridge:Bridge):
    bridge = to_bridge
    ctrl_logger.info(f" Agregando {vm.tag} '{vm.name}' al bridge {bridge.name}...")
    try:
        bridge.add_vm(vm)
        ctrl_logger.info(f" {vm.tag} '{vm.name}' agregado con exito")
    except LxcNetworkError as err:
        ctrl_logger.error(err)
    update_bridge(bridge)
    
        
        

