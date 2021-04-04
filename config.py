import subprocess
import logging
from tools import config_file
from os import remove
from time import sleep

logging.basicConfig(level=logging.NOTSET)
config_logger = logging.getLogger(__name__)   
        
def configVms():
    """Configures the IPV4 of the virtual machines and attaches them
    to their correspondent bridge"""
    config_logger.info(" Configurando maquinas virtuales...\n")
    config_logger.info(" Configurando balanceador de carga 'lb' (puente entre lxdbr0 y lxdbr1)...")
    for i in range(2):
        procExit = subprocess.call(["lxc", "network", "attach", f"lxdbr{i}", "lb", f"eth{i}"])
        if procExit == 0: 
            procExit = subprocess.call(["lxc","config","device",
                            "set","lb",f"eth{i}","ipv4.address",f"10.0.{i}.10"])
        if procExit == 1:
            config_logger.error(" Ha habido algun problema configurando" + 
                                    f" el balanceador de carga 'lb' con el bridge 'lxdbr{i}'")
        else:
            config_logger.info(f" Balanceador de carga 'lb' conectado con exito al bridge 'lxdbr{i}'")
    config_lb_netfile()  
    
    config_logger.info(" Configurando servidores (conectando a lxdbr0)...")
    rg = open("register.txt", "r")
    Vms = rg.read().split("\n") # same as [vm.strip() for vm in rg.readlines()]
    config_logger.debug(f" Servidores que configurar: {Vms}")
    for server in Vms:
        ipv4_address = f"10.0.0.{3 + Vms.index(server)}"
        config_logger.info(f" Configurando servidor '{server}'...")
        procExit = subprocess.call(["lxc", "network", "attach", "lxdbr0", server, "eth0"])
        if procExit == 0: 
            procExit = subprocess.call(["lxc","config","device",
                            "set",server,"eth0","ipv4.address",ipv4_address])
        if procExit == 1:
            config_logger.error(f" Ha habido algun problema configurando el server '{server}'")
        else:
            config_logger.info(f" Servidor '{server}' configurado con exito") 

def configBridges():
    """Configures the nat and address of 2 bridges. 
        The first one is not created because lxdbr0 is always created 
            when lxd is initializated 'lxd intit'"""
    config_logger.info(" Configurando bridges...")
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
    
def deleteBridgesConfig():
    """Deletes bridge lxdbr1 and the configutation of bridge lxdbr0 """
    config_logger.info(" Eliminando configuracion de bridges...")
    for i in range(2):
        bridge_name = f"lxdbr{i}"
        if i == 1:
            config_logger.info(f" Eliminando bridge '{bridge_name}'...")
            procExit = subprocess.call(["lxc", "network", "delete", bridge_name, "-q"])
            if procExit == 1:
                config_logger.error(f" No se ha podido eliminar el bridge '{bridge_name}'")
            else:
                config_logger.info(f" Bridge '{bridge_name}' eliminado con exito")
        else:
            subprocess.call(["lxc", "network", "set", bridge_name, "ipv4.address", "none"])
            subprocess.call(["lxc", "network", "set", bridge_name, "ipv4.nat", "false"])
            config_logger.info(f" La configuracion del bridge '{bridge_name}' (default) ha sido eliminada")
    if config_logger.level <= logging.INFO:
        subprocess.call(["lxc", "network","list"])

def config_lb_netfile():
    """Replace the configuration file of the load balancer with a new one"""
    config_logger.info(" Configurando net del balanceador de carga...")
    with open("50-cloud-init.yaml", "w") as file:
        file.write(config_file)
    # El problema esta en que lo crea pero al hacer start o debido a que no se ha inicializado todavia se crea el primer
    # fichero sobrescribiendo al nuestro
    subprocess.call(["lxc","start","lb"])
    error = "Error: not found"
    time = 0
    t0 = 0.5
    timeout = 10
    while "Error: not found" in error:
        if not time >= timeout:
            process = subprocess.Popen(["lxc","file","delete", "lb/etc/netplan/50-cloud-init.yaml"], stderr=subprocess.PIPE)
            error = process.communicate()[1].decode().strip()
            config_logger.debug(f"Intentando acceder a fichero de configuracion (stderr = '{error}') -> "
                                    + ("SUCCESS" if error == "" else "ERROR"))
            sleep(t0)
            time += t0
        else:
            subprocess.call(["lxc", "delete", "--force", "lb"])
            config_logger.error(" Error al añadir fichero de configuracion a 'lb' (timeout)\n")
            return        
    subprocess.call(["lxc","file","push","50-cloud-init.yaml", "lb/etc/netplan/50-cloud-init.yaml"])
    subprocess.call(["lxc","stop","lb"])
    config_logger.info(" Net del balanceador de carga configurada con exito\n")
    remove("50-cloud-init.yaml")
        
        
        
            