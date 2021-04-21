import logging
import subprocess
from time import sleep
from os import remove, path

from pickle import dump, load
from contextlib import suppress

import register.register as register
from utils.tools import objectlist_as_dict
from wrapper_classes.container import Container, LxcError

#------------------------ Command line functions -------------------------
#-------------------------------------------------------------------------
# This file contains custom bash functions for configuring virtual machines

# Tags of the containers available in this program
SERVER = "server"
LB = "load balancer"
CLIENT  = "client"

# Id del registro
ID = "containers"
image = "ubuntu1804"

def serialize(*servers) -> list:
    if register.load(ID) != None: return []
    vms = []
    lb = Container("lb", image, tag=LB)
    vms.append(lb)
    vms += serialize_servers(*servers)
    client = Container("client", image, tag=CLIENT)
    vms.append(client)
    return vms

def serialize_servers(*servers):
    servs = []
    if len(servers) == 0: return []
    j = 1
    vms = objectlist_as_dict(register.load(ID), key_attribute="name")
    if type(servers[0]) == int:
        numServs = servers[0]
        for i in range(numServs):
            try:
                name = servers[i+1] 
            except:
                # Si no nos han proporcionado nombre, buscamos uno que no exista ya
                name = f"s{j}"
                if vms != None:
                    while name in vms:
                        j += 1   
                        name = f"s{j}"
                j += 1
            servs.append(Container(name, image, tag=SERVER))
    else:
        for name in servers: 
            servs.append(Container(name, image, tag=SERVER))
    return servs

ctrl_logger = logging.getLogger(__name__)

def catch(func):
    def catched (*containers, **optionals):
        successful = []
        for c in containers:
            try:
                func(*containers, **optionals)
                successful.append(c)
            except LxcError as err:
                ctrl_logger.error(err)      
        return successful
    return catched


# -----------------------------------------------------------------------
def init(*containers, show_list=True):            
    successful = []
    for c in containers:
        try:
            ctrl_logger.info(f" Inicializando {c.tag} '{c.name}'...")
            c.init()
            ctrl_logger.info(f" {c.tag} '{c.name}' inicializado con exito")
            successful.append(c)
        except LxcError as err:
            ctrl_logger.error(err)      
           
    return successful
# -----------------------------------------------------------------------
def start(*containers, show_list=True):
    for c in containers:
        try:
            ctrl_logger.info(f" Arrancando {c.tag} '{c.name}'...")
            c.start()
            ctrl_logger.info(f" {c.tag} '{c.name}' arrancado con exito")
        except LxcError as err:
            ctrl_logger.error(err)
        
# --------------------------------------------------------------------------
def pause(*containers, show_list=True):
    """Stops the VMs (lb and servers) runned by startVMs()
            (Reads from register.txt which servers have been runned)"""
    for c in containers:
        try:
            ctrl_logger.info(f" Suspendiendo {c.tag} '{c.name}'...")
            c.pause()
            ctrl_logger.info(f" {c.tag} '{c.name}' suspendido con exito")
        except LxcError as err:
            ctrl_logger.error(err) 
# -----------------------------------------------------------------------
def stop(*containers, show_list=True):
    for c in containers:
        try:
            ctrl_logger.info(f" Deteniendo {c.tag} '{c.name}'...")
            c.stop()
            ctrl_logger.info(f" {c.tag} '{c.name}' detenido con exito")
        except LxcError as err:
            ctrl_logger.error(err) 

# -----------------------------------------------------------------------
def delete(*containers, show_list=True):
    """Deletes all virtual machine created if they are in a STOPPED state.
            (Reads from .register which servers have been created) and deletes them"""
    successful = []
    for c in containers:
        try:
            with suppress(Exception):
                c.stop()
            ctrl_logger.info(f" Eliminando {c.tag} '{c.name}'...")
            c.delete()
            ctrl_logger.info(f" {c.tag} '{c.name}' eliminado con exito")
            successful.append(c)
        except LxcError as err:
            ctrl_logger.error(err) 
        
    return successful
# --------------------------------------------------------------------------

def open_terminals(*containers):
    for c in containers:
        try:
            c.open_terminal()
        except LxcError as err:
            ctrl_logger.error(err)

def connect(c:Container, with_ip:str, to_network:str):
    ip, eth = with_ip, to_network
    ctrl_logger.info(f" Conectando {c.tag} '{c.name}' usando la ip '{ip}'" + 
                            f" a la network '{eth}'...")
    try:
        c.add_to_network(eth, ip)
        ctrl_logger.info(f" Conexion realizada con exito")
    except LxcError as err:
        ctrl_logger.error(err)
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
    ctrl_logger.info(f" Configurando el net_file del {c.tag} '{c.name}'... " +
                            "(Esta operacion puede tardar un rato dependiendo del PC " + 
                                "o incluso saltar el timeout si es muy lento)")
    ctrl_logger.debug("\n" + config_file)
    file_location = "bash/controllers/50-cloud-init.yaml"
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
            ctrl_logger.debug(f"Intentando acceder a fichero de configuracion de '{c.name}' (stderr = '{error}') -> "
                                    + ("SUCCESS" if error == "" else "ERROR"))
            sleep(t0)
            time += t0
        else:
            subprocess.call(["lxc","stop",c.name])
            #subprocess.call(["lxc", "delete", "--force", vm.name])
            ctrl_logger.error(f" Error al añadir fichero de configuracion a '{c.name}' (timeout)\n")
            remove(file_location)
            return        
    subprocess.call(["lxc","file","push",file_location, f"{c.name}/etc/netplan/50-cloud-init.yaml"])
    subprocess.call(["lxc","stop",c.name])
    ctrl_logger.info(f" Net del {c.tag} '{c.name}' configurada con exito\n")
    remove(file_location)
    update_container(c)
    
def update_container(c_to_update:Container):
    cs = register.load(register_id=ID)
    index = None
    for i, c in enumerate(cs):
        if c.name == c_to_update.name:
            index = i
            break
    if index != None:
        cs.pop(index)
        cs.append(c_to_update)
        register.update(ID, cs)