
import subprocess
import logging

logging.basicConfig(level=logging.NOTSET)
config_logger = logging.getLogger(__name__)   

def configVms():
    config_logger.info(" Configurando maquinas virtuales...\n")
    configBridges()
    configServers() 

def configBridges():
    """Configures the nat and address of 2 bridges. 
        The first one is not created because lxdbr0 is always created 
            when lxd is initializated 'lxd intit'"""
    for i in range(2):
        bridge_name = f"lxdbr{i}"
        ipv4_address = "10.0.0.1/24"
        if i == 1:
            ipv4_address = "10.0.1.1/24"
            config_logger.info(f" Creando bridge '{bridge_name}'...")
            procExit = subprocess.call(["lxc","network","create", bridge_name, "-q"])
            if procExit == 1:
                config_logger.error(f" Ha habido algun problema creando el bridge '{bridge_name}'")
                continue
            config_logger.info(f" Bridge '{bridge_name}' creado con exito")
        config_logger.info(f" Configurando bridge '{bridge_name}'...")
        procExit = subprocess.call(["lxc","network", "set", bridge_name, "ipv4.nat", "true"])
        if procExit == 1:
            config_logger.error(f" Ha habido algun problema configurando el bridge '{bridge_name}'")
            continue
        subprocess.call(["lxc", "network", "set", bridge_name, "ipv4.address", ipv4_address])
        subprocess.call(["lxc", "network", "set", bridge_name, "ipv6.nat", "false"])
        subprocess.call(["lxc", "network", "set", bridge_name, "ipv6.address", "none"])
        config_logger.info(f" El bridge '{bridge_name}' se ha configurado con exito")
    if config_logger.level <= logging.INFO:
        subprocess.call(["lxc", "network","list"])
    
def configServers():
    pass   
    
def deleteBridgesConfig():
    config_logger.info(" Eliminando configuracion de bridges...")
    for i in range(2):
        bridge_name = f"lxdbr{i}"
        if i == 1:
            config_logger.info(f" Eliminando bridge '{bridge_name}'...")
            procExit = subprocess.call(["lxc", "network", "delete", bridge_name, "-q"])
            if procExit == 1:
                config_logger.info(f" No se ha podido eliminar el bridge '{bridge_name}'")
            else:
                config_logger.info(f" Bridge '{bridge_name}' eliminado con exito")
        else:
            subprocess.call(["lxc", "network", "set", bridge_name, "ipv4.address", "none"])
            subprocess.call(["lxc", "network", "set", bridge_name, "ipv4.nat", "false"])
            config_logger.info(f" La configuracion del bridge '{bridge_name}' (default) se ha eliminado")
    if config_logger.level <= logging.INFO:
        subprocess.call(["lxc", "network","list"])
        
        
            