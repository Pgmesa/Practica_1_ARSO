import logging
import subprocess
from time import sleep
from os import remove, path
from functools import reduce
from pickle import dump, load
from contextlib import suppress

import register.register as register
from wrapper_classes.vm import VirtualMachine, LxcError

#------------------------ Command line functions -------------------------
#-------------------------------------------------------------------------
# This file contains custom bash functions for configuring virtual machines
root_logger = logging.getLogger()
ctrl_logger = logging.getLogger(__name__)

ID = "vms"
# -----------------------------------------------------------------------
def initVms(vms:list):
    """Creates the num of   servers specified and the load balancer,
            if they have not been initialized yet"""       
    if register.load(register_id=ID) != None:
        ctrl_logger.error(" Maquinas virtuales ya inicializadas, " +
                                "se deben destruir las anteriores para crear otras nuevas")
        return
    ctrl_logger.info(" Inicializando maquinas virtuales...\n")
    
    successful = []
    for vm in vms:
        try:
            ctrl_logger.info(f" Inicializando {vm.tag} '{vm.name}'...")
            vm.init()
            ctrl_logger.info(f" {vm.tag} '{vm.name}' inicializado con exito")
            successful.append(vm)
        except LxcError as err:
            ctrl_logger.error(err)
         
    register.add(ID, successful)
   
    if root_logger.level <= logging.WARNING:
        subprocess.call(["lxc", "list"])

# def addVms(*vm_names, num):
    
    
# -----------------------------------------------------------------------
def startVms(*vm_names):
    """Runs the Vms (lb and servers) initialized by createVMs(). 
            The server names created are logged in the register.txt file"""
    if register.load(register_id=ID) == None:
        ctrl_logger.error(" No existen maquinas virtuales creadas por el programa")
        return 
    empty = len(vm_names) == 0
    
    if empty:
        ctrl_logger.info(" Arrancando maquinas virtuales...\n")
        
    vms = register.load(register_id=ID) 
    notFound = list(vm_names)
    for vm in vms:
        if empty or vm.name in vm_names:
            try:
                ctrl_logger.info(f" Arrancando {vm.tag} '{vm.name}'...")
                vm.start()
                ctrl_logger.info(f" {vm.tag} '{vm.name}' arrancado con exito")
            except LxcError as err:
                ctrl_logger.error(err)     
            if not empty: notFound.remove(vm.name)   
    for name in notFound:
        ctrl_logger.error(f" La vm '{name}' no existe en este programa")

    register.update(ID, vms)

    if root_logger.level <= logging.WARNING:
        ctrl_logger.info(" Cargando resultados...")
        running = filter(lambda vm: vm.state == "RUNNING", vms)
        ips = reduce(lambda acum, vm: acum+len(vm.networks), running, 0)
        salida, t, twait, time_out= "", 0, 0.1, 10
        while not salida.count(".") == 3*ips:
            sleep(twait); t += twait
            if t >= time_out:
                ctrl_logger.error(" timeout del comando 'lxc list'")
                return
            out = subprocess.Popen(["lxc", "list"], stdout=subprocess.PIPE) 
            salida = out.stdout.read().decode()
            salida = salida[:-1] # Eliminamos el ultimo salto de linea
        print(salida)
# --------------------------------------------------------------------------
def pauseVms(*vm_names):
    """Stops the VMs (lb and servers) runned by startVMs()
            (Reads from register.txt which servers have been runned)"""
    if register.load(register_id=ID) == None:
        ctrl_logger.error(" No existen maquinas virtuales creadas por el programa")
        return 
    empty = len(vm_names) == 0
    
    if empty:
        ctrl_logger.info(" Suspendiendo maquinas virtuales...\n")
    
    vms = register.load(register_id=ID)
    notFound = list(vm_names)
    for vm in vms:
        if empty or vm.name in vm_names:
            try:
                ctrl_logger.info(f" Suspendiendo {vm.tag} '{vm.name}'...")
                vm.pause()
                ctrl_logger.info(f" {vm.tag} '{vm.name}' suspendido con exito")
            except LxcError as err:
                ctrl_logger.error(err) 
            if not empty: notFound.remove(vm.name)       
    for name in notFound:
        ctrl_logger.error(f" La vm '{name}' no existe en este programa")

    register.update(ID, vms)
    
    if root_logger.level <= logging.WARNING:
        subprocess.call(["lxc", "list"])
# -----------------------------------------------------------------------
def stopVms(*vm_names):
    """Stops the VMs (lb and servers) runned by startVMs()
            (Reads from register.txt which servers have been runned)"""
    if register.load(register_id=ID) == None:
        ctrl_logger.error(" No existen maquinas virtuales creadas por el programa")
        return 
    empty = len(vm_names) == 0
    
    if empty:
        ctrl_logger.info(" Deteniendo maquinas virtuales...\n")
    
    vms = register.load(register_id=ID)
    notFound = list(vm_names)
    for vm in vms:
        if empty or vm.name in vm_names:
            try:
                ctrl_logger.info(f" Deteniendo {vm.tag} '{vm.name}'...")
                vm.stop()
                ctrl_logger.info(f" {vm.tag} '{vm.name}' detenido con exito")
            except LxcError as err:
                ctrl_logger.error(err)  
            if not empty: notFound.remove(vm.name)      
    for name in notFound:
        ctrl_logger.error(f" La vm '{name}' no existe en este programa")

    register.update(ID, vms)
    
    if root_logger.level <= logging.WARNING:
        subprocess.call(["lxc", "list"])
# -----------------------------------------------------------------------
def deleteVms(*vm_names):
    """Deletes all virtual machine created if they are in a STOPPED state.
            (Reads from register.txt which servers have been created) and deletes them"""
    if register.load(register_id=ID) == None:
        ctrl_logger.error(" No existen maquinas virtuales creadas por el programa")
        return 
    empty = len(vm_names) == 0
    
    if empty:
        ctrl_logger.info(" Eliminando maquinas virtuales...\n")
    
    vms = register.load(register_id=ID)
    failures = []
    success = []
    not_deleted = []
    notFound = list(vm_names)
    for vm in vms:
        if empty or vm.name in vm_names:
            with suppress(LxcError):
                vm.stop()
            try:
                ctrl_logger.info(f" Eliminando {vm.tag} '{vm.name}'...")
                vm.delete()
                success.append(vm)
                ctrl_logger.info(f" {vm.tag} '{vm.name}' eliminado con exito")
            except LxcError as err:
                failures.append(vm)
                ctrl_logger.error(err)  
            if not empty: notFound.remove(vm.name) 
        else:
            not_deleted.append(vm)
    for name in notFound:
        ctrl_logger.error(f" La vm '{name}' no existe en este programa")
    
    if len(success) == len(vms):
        register.remove(register_id=ID)
    else:
        register.update(ID, not_deleted+failures)
        
    if root_logger.level <= logging.WARNING:
        subprocess.call(["lxc", "list"])
# --------------------------------------------------------------------------

def open_vms_terminal(*vm_names):
    if register.load(register_id=ID) == None:
        ctrl_logger.error(" No existen maquinas virtuales creadas por el programa")
        return 
    vms = register.load(register_id=ID)
    empty = len(vm_names) == 0
    notFound = list(vm_names)
    for vm in vms:
        if empty or vm.name in vm_names:
            try:
                vm.open_terminal()
            except LxcError as err:
                ctrl_logger.error(err)  
            if not empty: notFound.remove(vm.name)          
    for name in notFound:
        ctrl_logger.error(f" La vm '{name}' no existe en este programa")

def connect(vm:VirtualMachine, with_ip:str, to_network:str):
    ip, eth = with_ip, to_network
    ctrl_logger.info(f" Conectando {vm.tag} '{vm.name}' usando la ip '{ip}'" + 
                            f" a la network '{eth}'...")
    try:
        vm.add_to_network(eth, ip)
        ctrl_logger.info(f" Conexion realizada con exito")
    except LxcError as err:
        ctrl_logger.error(err)
    update_vm(vm)


def configure_netfile(vm:VirtualMachine):
    """Replace the configuration file with a new one"""
    networks = vm.networks
    if len(networks) == 1 and list(networks.keys())[0] == "eth0": return
    
    config_file =("network:\n" +
                  "    version: 2\n" + 
                  "    ethernets:\n")
    for eth in networks:
        new_eth_config = (f"        {eth}:\n" + 
                            "            dhcp4: true\n")
        config_file += new_eth_config
    ctrl_logger.info(f" Configurando el net_file del {vm.tag} '{vm.name}'... " +
                            "(Esta operacion puede tardar un rato dependiendo del PC " + 
                                "o incluso saltar el timeout si es muy lento)")
    ctrl_logger.debug("\n" + config_file)
    file_location = "controllers/50-cloud-init.yaml"
    with open(file_location, "w") as file:
        file.write(config_file)
    # El problema esta en que lo crea pero al hacer start o debido a que no se ha inicializado todavia se crea el primer
    # fichero sobrescribiendo al nuestro
    subprocess.run(["lxc","start",vm.name])
    error = "Error: not found"
    time = 0
    t0 = 2
    timeout = 60
    while "Error: not found" in error:
        if not time >= timeout:
            process = subprocess.Popen(
                ["lxc","file","delete", f"{vm.name}/etc/netplan/50-cloud-init.yaml"],
                stderr=subprocess.PIPE
            )
            error = process.communicate()[1].decode().strip()
            ctrl_logger.debug(f"Intentando acceder a fichero de configuracion de '{vm.name}' (stderr = '{error}') -> "
                                    + ("SUCCESS" if error == "" else "ERROR"))
            sleep(t0)
            time += t0
        else:
            subprocess.call(["lxc","stop",vm.name])
            #subprocess.call(["lxc", "delete", "--force", vm.name])
            ctrl_logger.error(f" Error al añadir fichero de configuracion a '{vm.name}' (timeout)\n")
            remove(file_location)
            return        
    subprocess.call(["lxc","file","push",file_location, f"{vm.name}/etc/netplan/50-cloud-init.yaml"])
    subprocess.call(["lxc","stop",vm.name])
    ctrl_logger.info(f" Net del {vm.tag} '{vm.name}' configurada con exito\n")
    remove(file_location)
    update_vm(vm)
    
def update_vm(vm_to_update:VirtualMachine):
    vms = register.load(register_id=ID)
    index = None
    for i, vm in enumerate(vms):
        if vm.name == vm_to_update.name:
            index = i
            break
    if index != None:
        vms.pop(index)
        vms.append(vm_to_update)
        register.update(ID, vms)