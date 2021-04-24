
import logging

import dependencies.register.register as register
from dependencies.utils.decorators import catch_foreach
from dependencies.lxc_classes.bridge import Bridge, LxcNetworkError

# Id del registro
ID = "bridges"
bgs_logger = logging.getLogger(__name__)
# -------------------------------------------------------------------
@catch_foreach(bgs_logger)
def init(b:Bridge=None):
    bgs_logger.info(f" Creando bridge '{b.name}'...")
    b.create()
    bgs_logger.info(f" bridge '{b.name}' creado con exito")
    add_bridge(b)

# -------------------------------------------------------------------
@catch_foreach(bgs_logger)
def delete(b:Bridge):
    bgs_logger.info(f" Eliminando bridge '{b.name}'...")
    b.delete()
    bgs_logger.info(f"  bridge '{b.name}' eliminado con exito")
    update_bridge(b, remove=True)
# -------------------------------------------------------------------

# -------------------------------------------------------------------
def attach(vm_name:str, to_bridge:Bridge):
    bridge = to_bridge
    msg = f" Agregando '{vm_name}' al bridge {bridge.name}..."
    bgs_logger.info(msg)
    try:
        bridge.add_vm(vm_name)
        bgs_logger.info(f" '{vm_name}' agregado con exito")
    except LxcNetworkError as err:
        bgs_logger.error(err)
    update_bridge(bridge)
    
# -------------------------------------------------------------------   
def update_bridge(b_to_update:Bridge, remove=False):
    bgs = register.load(register_id=ID)
    index = None
    for i, b in enumerate(bgs):
        if b.name == b_to_update.name:
            index = i
            break
    if index != None:
        bgs.pop(index)
        if remove:
            if len(bgs) == 0:
                register.remove(ID)
                return
        else:
            bgs.append(b_to_update)
        register.update(ID, bgs)

def add_bridge(b_to_add:Bridge):
    cs = register.load(register_id=ID)
    if cs == None:
        register.add(ID, [b_to_add])
    else:
        register.update(ID, b_to_add, override=False)
        
# -------------------------------------------------------------------      

