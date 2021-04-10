import subprocess
import logging
from os import remove, path
from vms.config import configVms, configBridges, deleteBridgesConfig
from vms.vm import VirtualMachine, LxcError
from pickle import dump, load

#------------------------ Command line functions -------------------------
#-------------------------------------------------------------------------
# This file contains custom bash functions for configuring virtual machines
logging.basicConfig(level=logging.NOTSET)
ctrl_logger = logging.getLogger(__name__)
    
# ------------------------------ cmd crear ------------------------------
# -----------------------------------------------------------------------
def initVms(vms:list):
    """Creates the num of   servers specified and the load balancer,
            if they have not been initialized yet"""       
    if path.isfile("register"):
        ctrl_logger.warning(" Maquinas virtuales ya inicializadas, " +
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
         
    with open("register", "wb") as file:
        dump(successful, file)
    
    if ctrl_logger.level <= logging.INFO:
        subprocess.call(["lxc", "list"])
        
    # configBridges()
    # configVms()
    
# -----------------------------------------------------------------------

# ------------------------------ cmd arrancar ------------------------------
# --------------------------------------------------------------------------
def startVms():
    """Runs the Vms (lb and servers) initialized by createVMs(). 
            The server names created are logged in the register.txt file"""
    if not path.isfile("register"):
        ctrl_logger.warning(" No existen maquinas virtuales creadas por el programa")
        return
    ctrl_logger.info(" Arrancando maquinas virtuales...\n")
    
    with open("register", "rb") as file:
        vms = load(file)
    
    for vm in vms:
        try:
            ctrl_logger.info(f" Arrancando {vm.tag} '{vm.name}'...")
            vm.start()
            ctrl_logger.info(f" {vm.tag} '{vm.name}' arrancado con exito")
        except LxcError as err:
            ctrl_logger.error(err)

    with open("register", "wb") as file:
        dump(vms, file)

    if ctrl_logger.level <= logging.INFO:
        salida = ""
        while not salida.count(".") == 3*(len(vms)):
            out = subprocess.Popen(["lxc", "list"], stdout=subprocess.PIPE) 
            salida = out.communicate()[0].decode()
            salida = salida[:-1] # Eliminamos el ultimo salto de linea
        print(salida)
# --------------------------------------------------------------------------

# ------------------------------ cmd parar ------------------------------
# -----------------------------------------------------------------------
def stopVms():
    """Stops the VMs (lb and servers) runned by startVMs()
            (Reads from register.txt which servers have been runned)"""
    if not path.isfile("register"):
        ctrl_logger.warning(" No existen maquinas virtuales creadas por el programa")
        return
    ctrl_logger.info(" Deteniendo maquinas virtuales...\n")
    
    with open("register", "rb") as file:
        vms = load(file)
    
    for vm in vms:
        try:
            ctrl_logger.info(f" Deteniendo {vm.tag} '{vm.name}'...")
            vm.stop()
            ctrl_logger.info(f" {vm.tag} '{vm.name}' detenido con exito")
        except LxcError as err:
            ctrl_logger.error(err)

    with open("register", "wb") as file:
        dump(vms, file)
    
    if ctrl_logger.level <= logging.INFO:
        subprocess.call(["lxc", "list"])
# -----------------------------------------------------------------------

# ------------------------------ cmd destruir ------------------------------
# --------------------------------------------------------------------------
def deleteVms():
    """Deletes all virtual machine created if they are in a STOPPED state.
            (Reads from register.txt which servers have been created) and deletes them"""
    if not path.isfile("register"):
        ctrl_logger.warning(" No existen maquinas virtuales creadas por el programa")
        return
    ctrl_logger.info(" Eliminando maquinas virtuales...\n")
    
    with open("register", "rb") as file:
        vms = load(file)
    
    failures = []
    for vm in vms:
        try:
            ctrl_logger.info(f" Eliminando {vm.tag} '{vm.name}'...")
            vm.delete()
            ctrl_logger.info(f" {vm.tag} '{vm.name}' eliminado con exito")
        except LxcError as err:
            failures.append(vm)
            ctrl_logger.error(err)
   
    if len(failures) > 0:
        with open("register", "wb") as file:
            dump(failures, file)
    else:
        remove("register")
        
    if ctrl_logger.level <= logging.INFO:
        subprocess.call(["lxc", "list"])
    #deleteBridgesConfig() 
# --------------------------------------------------------------------------