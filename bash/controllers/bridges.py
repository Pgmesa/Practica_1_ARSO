import logging
import subprocess
from os import remove, path

import register.register as register
from wrapper_classes.bridge import Bridge, LxcNetworkError

# -----------------------------------------------

ctrl_logger = logging.getLogger(__name__)

ID = "bridges"

def serialize(numBridges:int) -> list:
    if register.load(ID) != None: return []
    bridges = []
    for i in range(numBridges):
        b_name = f"lxdbr{i}"
        b = Bridge(
            b_name, 
            ethernet=f"eth{i}",
            ipv4_nat=True, ipv4_addr=f"10.0.{i}.1/24"
        )
        bridges.append(b)
    return bridges

# -------------------------------------------------

def init(*bridges, show_list=True):
    successful = []
    for b in bridges:
        try:
            ctrl_logger.info(f" Creando bridge '{b.name}'...")
            b.create()
            ctrl_logger.info(f" bridge '{b.name}' creado con exito")
            successful.append(b)
        except LxcNetworkError as err:
            ctrl_logger.error(err)
    
    if len(successful) == 0:
        return None    
    return successful


def delete(*bridges, show_list=True):
    successful = []
    for b in bridges:
        try:
            ctrl_logger.info(f" Eliminando bridge '{b.name}'...")
            b.delete()
            ctrl_logger.info(f"  Bridge '{b.name}' eliminado con exito")
            successful.append(b)
        except LxcNetworkError as err:
            ctrl_logger.error(err) 
        
    return successful

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
        

