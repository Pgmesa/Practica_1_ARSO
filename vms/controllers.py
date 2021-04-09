import subprocess
import logging
from os import remove, path
from vms.config import configVms, configBridges, deleteBridgesConfig
 
#------------------------ Command line functions -------------------------
#-------------------------------------------------------------------------
# This file contains custom bash functions for configuring virtual machines
logging.basicConfig(level=logging.NOTSET)
ctrl_logger = logging.getLogger(__name__)

# ------------------------------ cmd crear ------------------------------
# -----------------------------------------------------------------------
def createVms(numServs:int):
    """Creates the num of servers specified and the load balancer,
            if they have not been initialized yet"""       
    if path.isfile("register.txt"):
        ctrl_logger.warning(" Maquinas virtuales ya inicializadas, " +
                                "se deben destruir las anteriores para crear otras nuevas")
        return
    ctrl_logger.info(" Creando maquinas virtuales...\n")
    createLoadBalancer()
    createServer(numServs)
    # createClient()
    if ctrl_logger.level <= logging.INFO:
        subprocess.call(["lxc", "list"])
    configBridges()
    configVms()

def createLoadBalancer():
    """Initializes the load balancer"""
    ctrl_logger.info(" Creando el balanceador de carga...")
    procExit = subprocess.call(["lxc", "init", "ubuntu1804", "lb", "-q"])
    if procExit == 0:
        ctrl_logger.info(" El balanceador de carga 'lb' ha sido creado con exito\n")
    else:
        ctrl_logger.error(" Ha habido algun problema creando el balanceador de carga 'lb'\n")
 
def createServer(numServs:int):
    """Initializes 'numServs' virtual machines and writes
            their names in register.txt"""
    ctrl_logger.info(f" Creando {numServs} servidor{'' if numServs==1 else 'es'}...")
    rg = open("register.txt", "w")
    for i in range(numServs):
        name = f"s{i+1}"
        ctrl_logger.info(f" Creando servidor {i+1} con nombre '{name}'...")
        procExit = subprocess.call(["lxc", "init", "ubuntu1804", name, "-q"])
        if procExit == 0:
            last = i == numServs - 1
            rg.write(name if last else name+"\n")
            ctrl_logger.info(f" Servidor {i+1} '{name}' creado con exito")
        else:
            ctrl_logger.error(f" Ha habido algun problema creando el servidor {i+1} '{name}'")
    rg.close()
# -----------------------------------------------------------------------

# ------------------------------ cmd arrancar ------------------------------
# --------------------------------------------------------------------------
def startVms():
    """Runs the Vms (lb and servers) initialized by createVMs(). 
            The server names created are logged in the register.txt file"""
    if not path.isfile("register.txt"):
        ctrl_logger.warning(" No existen maquinas virtuales creadas por el programa")
        return
    ctrl_logger.info(" Arrancando maquinas virtuales...\n")
    ctrl_logger.info(" Arrancando el balanceador de carga..." )        
    procExit = subprocess.call(["lxc", "start", "lb"])
    if procExit == 0:
        ctrl_logger.info(f" El balanceador de carga 'lb' ha sido arrancado correctamente\n")
        subprocess.Popen([
                            "xterm","-fa", "monaco", "-fs", "13", "-bg", "black",
                            "-fg", "green", "-e", f"lxc exec lb bash"
                            ])
    else:
        ctrl_logger.error(f" Ha habido algun problema arrancando el balanceador de carga 'lb' \n")     
             
    ctrl_logger.info(" Arrancando servidores...")
    rg = open("register.txt", "r")
    VMs = rg.read().split("\n") # same as [vm.strip() for vm in rg.readlines()]
    ctrl_logger.debug(f" Servidores que arrancar: {VMs}")
    for vm in VMs:
        procExit = subprocess.call(["lxc", "start", vm])
        if procExit == 0:
            ctrl_logger.info(f" Servidor '{vm}' arrancado correctamente ")
            subprocess.Popen([
                                "xterm","-fa", "monaco", "-fs", "13", "-bg", "black",
                                "-fg", "green", "-e", f"lxc exec {vm} bash"
                                ])
        else:
            ctrl_logger.error(f" Ha habido algun problema arrancando el servidor '{vm}'")
    rg.close()
    if ctrl_logger.level <= logging.INFO:
        salida = ""
        while not salida.count(".") == 3*(len(VMs)+2):
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
    if not path.isfile("register.txt"):
        ctrl_logger.warning(" No existen maquinas virtuales creadas por el programa")
        return
    ctrl_logger.info(" Deteniendo maquinas virtuales...\n")
    ctrl_logger.info(" Deteniendo el balanceador de carga..." )        
    procExit = subprocess.call(["lxc", "stop", "lb"])
    if procExit == 0:
        ctrl_logger.info(f" El balanceador de carga 'lb' ha sido detenido correctamente\n")
    else:
        ctrl_logger.error(f" Ha habido algun problema deteniendo el balanceador de carga 'lb'\n") 
        
    ctrl_logger.info(" Deteniendo servidores...")
    rg = open("register.txt", "r")
    VMs = rg.read().split("\n") # same as [vm.strip() for vm in rg.readlines()]
    ctrl_logger.debug(f" Servidores que detener: {VMs}")
    for vm in VMs:
        procExit = subprocess.call(["lxc", "stop", vm])
        if procExit == 0:
            ctrl_logger.info(f" Servidor '{vm}' detenido correctamente ")
        else:
            ctrl_logger.error(f" Ha habido algun problema deteniendo el servidor '{vm}'")
    rg.close()
    if ctrl_logger.level <= logging.INFO:
        subprocess.call(["lxc", "list"])
# -----------------------------------------------------------------------

# ------------------------------ cmd destruir ------------------------------
# --------------------------------------------------------------------------
def deleteVms():
    """Deletes all virtual machine created if they are in a STOPPED state.
            (Reads from register.txt which servers have been created) and deletes them"""
    if not path.isfile("register.txt"):
        ctrl_logger.warning(" No existen maquinas virtuales creadas por el programa")
        return
    ctrl_logger.info(" Eliminando maquinas virtuales...\n")
    ctrl_logger.info(" Eliminando balanceador de carga...")
    procExit = subprocess.call(["lxc", "delete","lb"])
    if procExit == 0:
        ctrl_logger.info(f" El balanceador de carga 'lb' ha sido eliminado correctamente\n")
    else:
        ctrl_logger.error(f" Ha habido algun problema eliminando el balanceador de carga 'lb'\n")
    
    ctrl_logger.info(" Eliminando servidores...")
    rg = open("register.txt", "r")
    VMs = rg.read().split("\n") # same as [vm.strip() for vm in rg.readlines()]
    ctrl_logger.debug(f" Servidores que destruir: {VMs}")
    failures = []
    for vm in VMs:
        procExit = subprocess.call(["lxc", "delete", vm])
        if procExit == 0:
            ctrl_logger.info(f" Servidor '{vm}' eliminado correctamente")
        else:
            failures.append(vm)
            ctrl_logger.error(f" Ha habido algun problema eliminando el servidor '{vm}'")
    rg.close()
   
    if len(failures) > 0:
        rg = open("register.txt", "w")
        for f in failures: 
            last = failures.index(f) == len(failures)-1
            rg.write(f if last else f +"\n")
        rg.close()
    else:
        remove("register.txt")
    if ctrl_logger.level <= logging.INFO:
        subprocess.call(["lxc", "list"])
    deleteBridgesConfig() 
# --------------------------------------------------------------------------