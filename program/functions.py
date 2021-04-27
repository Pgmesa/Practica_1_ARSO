
import os
import re
import logging
import platform
import subprocess
from time import sleep
from functools import reduce
from math import floor

import program.controllers.bridges as bridges
import program.controllers.containers as containers
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
        ["display", "program/resources/diagram.png"],
        stdout=subprocess.PIPE
    ) 
def show_files_structure():
    subprocess.Popen(
        ["display", "program/resources/files_structure.png"],
        stdout=subprocess.PIPE
    )
    subprocess.Popen(
        ["display", "program/resources/external_dependencies.png"],
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
    try:
        subprocess.run(
            ["xterm", "--version"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
    except:
        warn = (" xterm is not installed in this computer, and some " +
              "functionalities may require this module, please enter " +
              "'sudo apt install xterm' for installing it")
        program_logger.warning(warn)
    # Inicializamos lxd y ejecutamos si no existe el profile default
    process = subprocess.run(
        ["lxc", "profile", "list"],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    if "default" not in process.stdout.decode():
        program_logger.info(" Inicializando lxd...")
        subprocess.run(["lxd", "init", "--auto"])
        program_logger.info(" lxd inicializado...")

def check_updates():
    """Futura implementacion para detectar cambios que se hayan podido
    producir en los contenedores y bridges desde fuera del programa
    y actualizar las instancia guardadas en el registro"""
    process = subprocess.run(
        ["lxc", "list"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    cs_info = lxclist_as_dict(process.stdout.decode())
    cs_object = register.load(containers.ID)
    # Detecamos los cambios que se hayan producido fuera del programa
    # de los contenedores
    cs_updated = []
    for c in cs_object:
        if c.name not in cs_info["NAME"]:
            warn = (f" El contenedor {c.name} se ha eliminado fuera " +
                    "del programa (informacion actualizada)")
            program_logger.warning(warn)
            continue
        index = cs_info["NAME"].index(c.name)
        if c.state != cs_info["STATE"][index]:
            new_state = cs_info["STATE"][index]
            warn = (f" El contenedor {c.name} se ha modificado fuera " +
                   f"del programa, ha pasado de {c.state} a " + 
                   f"{new_state} (informacion actualizada)")
            c.state = new_state
            program_logger.warning(warn)
        if c.state == "RUNNING":
            new = cs_info["IPV4"][index]
            splitted = re.split(r"\(| |\)", new)
            while "" in splitted:
                splitted.remove("")
            new_ipv4, new_eth = splitted
            for eth, ip in c.networks.items():
                if ip != new_ipv4:
                    warn = (f" La ipv4 del contenedor {c.name} se ha " +
                            f"modificado fuera del programa, ha pasado " + 
                            f"de {ip}:{eth} a {new_ipv4}:{new_eth} " +
                             "(informacion actualizada)")
                    c.networks[new_eth] = new_ipv4
                    program_logger.warning(warn)
        cs_updated.append(c)
    register.update(containers.ID, cs_updated)

# --------------------------------------------------------------------  
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
    
def lxclist_as_dict(string:str):
    info = {}
    chars = list(string)
    cells = -1
    line_length = 0
    cells_length = []
    cell_start = 0
    for i, c in enumerate(chars):
        if c == "|":
            break
        line_length = 1 + i
        if c == "+":
            cells += 1
            if cells > 0:
                cells_length.append(line_length-1-cell_start)
            cell_start = 1 + i
            continue  
    lines = len(chars)/line_length
    rows = floor(lines/2)
    
    _start = line_length + 1
    for i in range(cells):
        if i != 0:
            _start += cells_length[i-1] + 1
        _end = _start + cells_length[i]
        key = string[_start:_end].strip()
        info[key] = []
        for j in range(rows):
            start = _start + line_length*(2*(j+1))
            if start < len(chars):
                end = start + cells_length[i]
                value = string[start:end].strip()
                info[key].append(value)
    return info

# --------------------------------------------------------------------