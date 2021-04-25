
import os
import logging
import platform
import subprocess
from time import sleep
from functools import reduce

import program.controllers.bridges as bridges
import program.controllers.containers as containers
import program.machines as machines
import dependencies.register.register as register
from dependencies.utils.tools import pretty, objectlist_as_dict

class ProgramError(Exception):
    pass

program_logger = logging.getLogger(__name__)
# --------------------------------------------------------------------
def connect_machines():
    # Si no hay puentes a los que conectar salimos
    bgs = objectlist_as_dict(
        register.load(bridges.ID),
        key_attribute="name"
    )
    if bgs == None: return
    # Si no hay vms creadas que conectar salimos
    cs = register.load(containers.ID)
    if cs == None: return
    
    j = 0
    existing_ips = []
    for c in cs:
        existing_ips += c.networks.values()
    for c in cs:
        # Si ya se ha conectado continuamos con la siguiente
        if len(c.networks) > 0: continue
        bridges_to_connect = []
        if c.tag == "server" or c.tag == "load balancer":
            if "lxdbr0" in bgs:
                bridges_to_connect.append(bgs['lxdbr0'])
        if c.tag == "client" or c.tag == "load balancer":
            if "lxdbr1" in bgs:
                bridges_to_connect.append(bgs['lxdbr1'])
        for b in bridges_to_connect:
            # Asiganamos una ip que no exista todavia
            ip = f"{b.ipv4_addr[:-4]}{j+10}"
            while ip in existing_ips:
                j += 1    
                ip = f"{b.ipv4_addr[:-4]}{j+10}"  
            existing_ips.append(ip)
            bridges.attach(c.name, to_bridge=b)
            containers.connect(
                c,
                with_ip=ip,
                to_network=b.ethernet
            )
        containers.configure_netfile(c)

def update_conexions():
    bgs = register.load(register_id=bridges.ID)
    if bgs == None: return
    cs = register.load(register_id=containers.ID)
    if cs == None:
        names_existing_cs = []
    else:
        names_existing_cs = list(map(lambda c: c.name, cs))
    
    for b in bgs:
        deleted = []
        for c_name in b.used_by:
            if c_name not in names_existing_cs:
                deleted.append(c_name)
        for d in deleted:
            b.used_by.remove(d)
    register.update(bridges.ID, bgs)
    
# --------------------------------------------------------------------
def print_state():
    cs = register.load(register_id=containers.ID)
    bgs = register.load(register_id=bridges.ID)
    print("VIRTUAL MACHINES")
    if cs != None:
        for c in cs:
            print(pretty(c))
    else:
        print("No containers created by the program")
    print("BRIDGES")
    if bgs != None:       
        for b in bgs:
            print(pretty(b))
    else:
        print("No bridges created by the program")
        
def show_diagram():
    subprocess.Popen(
        ["display", "program/resources/images/diagram.png"],
        stdout=subprocess.PIPE
    ) 
# --------------------------------------------------------------------   
  
def check_enviroment():
    system = platform.system()
    program_logger.debug(f" {system} OS detected")
    if system != "Linux":
        err = f" This program only works on Linux -> {system} OS detected"
        raise ProgramError(err)
    try:
        subprocess.run(
            ["lxd", "--version"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
    except:
        err = (" 'lxd' is not installed in this computer and it's necessary " +
               "for the execution of this program.\nEnter 'sudo apt " +
               "install lxd' in the commands terminal for installing it.")
        raise ProgramError(err)
  
def lxc_list():
    cs = register.load(containers.ID)
    program_logger.info(" Cargando resultados...")
    if cs == None:
        subprocess.call(["lxc", "list"]) 
        return
    running = list(filter(lambda c: c.state == "RUNNING", cs))
    frozen = list(filter(lambda c: c.state == "FROZEN", cs))
    total = running+frozen
    if len(total) == 0:
        subprocess.call(["lxc", "list"]) 
        return
    ips = reduce(lambda acum, c: acum+len(c.networks), total, 0)
    salida, t, twait, time_out= "", 0, 0.1, 10
    while not salida.count(".") == 3*ips:
        sleep(twait); t += twait
        if t >= time_out:
            program_logger.error(" timeout del comando 'lxc list'")
            return
        out = subprocess.Popen(["lxc", "list"], stdout=subprocess.PIPE) 
        salida = out.stdout.read().decode()
        salida = salida[:-1] # Eliminamos el ultimo salto de linea
    print(salida)

def lxc_network_list():
    subprocess.call(["lxc", "network", "list"])
    
# --------------------------------------------------------------------