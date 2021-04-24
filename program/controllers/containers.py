
import logging
import subprocess
from time import sleep
from os import remove
from contextlib import suppress

import dependencies.register.register as register
from dependencies.utils.tools import objectlist_as_dict
from dependencies.utils.decorators import catch_foreach
from dependencies.lxc_classes.container import Container, LxcError

ID = "containers"
cs_logger = logging.getLogger(__name__)
# --------------------------------------------------------------------
@catch_foreach(cs_logger)
def init(c:Container=None):            
    cs_logger.info(f" Inicializando {c.tag} '{c.name}'...")
    c.init()
    cs_logger.info(f" {c.tag} '{c.name}' inicializado con exito")
    add_container(c)
    
# --------------------------------------------------------------------
@catch_foreach(cs_logger)
def start(c:Container):
    cs_logger.info(f" Arrancando {c.tag} '{c.name}'...")
    c.start()
    cs_logger.info(f" {c.tag} '{c.name}' arrancado con exito")
    update_container(c)
        
# --------------------------------------------------------------------
@catch_foreach(cs_logger)
def pause(c:Container):
    cs_logger.info(f" Suspendiendo {c.tag} '{c.name}'...")
    c.pause()
    cs_logger.info(f" {c.tag} '{c.name}' suspendido con exito")
    update_container(c)
        
# --------------------------------------------------------------------
@catch_foreach(cs_logger)
def stop(c:Container):
    cs_logger.info(f" Deteniendo {c.tag} '{c.name}'...")
    c.stop()
    cs_logger.info(f" {c.tag} '{c.name}' detenido con exito")
    update_container(c)

# --------------------------------------------------------------------
@catch_foreach(cs_logger)
def delete(c:Container):
    with suppress(Exception):
        c.stop()
    cs_logger.info(f" Eliminando {c.tag} '{c.name}'...")
    c.delete()
    cs_logger.info(f" {c.tag} '{c.name}' eliminado con exito")
    update_container(c, remove=True)

# --------------------------------------------------------------------
@catch_foreach(cs_logger)
def open_terminal(c:Container):
    c.open_terminal()
        
# --------------------------------------------------------------------
def connect(c:Container, with_ip:str, to_network:str):
    ip, eth = with_ip, to_network
    cs_logger.info(f" Conectando {c.tag} '{c.name}' usando la " + 
                            f"ip '{ip}' a la network '{eth}'...")
    try:
        c.add_to_network(eth, ip)
        cs_logger.info(f" Conexion realizada con exito")
    except LxcError as err:
        cs_logger.error(err)
    update_container(c)

def configure_netfile(c:Container):
    """Replace the configuration file with a new one"""
    networks = c.networks
    if len(networks) == 1 and list(networks.keys())[0] == "eth0": return
    
    config_file =("network:\n" +
                  "    version: 2\n" + 
                  "    ethernets:\n")
    for eth in networks:
        new_eth_config = (f"        {eth}:\n" + 
                            "            dhcp4: true\n")
        config_file += new_eth_config
    cs_logger.info(f" Configurando el net_file del {c.tag} '{c.name}'... " +
                            "(Esta operacion puede tardar un rato dependiendo del PC " + 
                                "o incluso saltar el timeout si es muy lento)")
    cs_logger.debug("\n" + config_file)
    file_location = "50-cloud-init.yaml"
    with open(file_location, "w") as file:
        file.write(config_file)
    # El problema esta en que lo crea pero al hacer start o debido a que no se ha inicializado todavia se crea el primer
    # fichero sobrescribiendo al nuestro
    subprocess.run(["lxc","start",c.name])
    error = "Error: not found"
    time = 0
    t0 = 2
    timeout = 60
    while "Error: not found" in error:
        if not time >= timeout:
            process = subprocess.Popen(
                ["lxc","file","delete", f"{c.name}/etc/netplan/50-cloud-init.yaml"],
                stderr=subprocess.PIPE
            )
            error = process.communicate()[1].decode().strip()
            cs_logger.debug(f"Intentando acceder a fichero de configuracion de '{c.name}' (stderr = '{error}') -> "
                                    + ("SUCCESS" if error == "" else "ERROR"))
            sleep(t0)
            time += t0
        else:
            subprocess.call(["lxc","stop",c.name])
            #subprocess.call(["lxc", "delete", "--force", vm.name])
            cs_logger.error(f" Error al añadir fichero de configuracion a '{c.name}' (timeout)")
            remove(file_location)
            return        
    subprocess.call(["lxc","file","push",file_location, f"{c.name}/etc/netplan/50-cloud-init.yaml"])
    subprocess.call(["lxc","stop",c.name])
    cs_logger.info(f" Net del {c.tag} '{c.name}' configurada con exito")
    remove(file_location)
    update_container(c)
    
# --------------------------------------------------------------------    
def update_container(c_to_update:Container, remove:bool=False):
    cs = register.load(ID)
    index = None
    for i, c in enumerate(cs):
        if c.name == c_to_update.name:
            index = i
            break
    if index != None:
        cs.pop(index)
        if remove:
            if len(cs) == 0:
                register.remove(ID)
                return
        else:
            cs.append(c_to_update)
        register.update(ID, cs)

def add_container(c_to_add:Container):
    cs = register.load(register_id=ID)
    if cs == None:
        register.add(ID, [c_to_add])
    else:
        register.update(ID, c_to_add, override=False)
    
# --------------------------------------------------------------------
