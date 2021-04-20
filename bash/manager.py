
from os import path

from utils.tools import pretty, objectlist_as_dict
import register.register as register
from wrapper_classes.bridge import Bridge
from wrapper_classes.vm import VirtualMachine
import controllers.vms_handler as vms_handler
import controllers.bridges_handler as bridges_handler

# Clase que se encarga de coordinar los dos controladores
# (Los cuales no interaccionan entre ellos de por si)

# Tags of the Machines available in this program
SERVER = "server"
LB = "load balancer"
CLIENT  = "client"

image = "ubuntu1804"

def connect_machines(*vms):
    bridges = objectlist_as_dict(register.load(bridges_handler.ID), key_attribute="name")
    j = 0
    for vm in vms:
        bridges_to_connect = []
        if vm.tag == SERVER or vm.tag == LB:
            if "lxdbr0" in bridges:
                bridges_to_connect.append(bridges['lxdbr0'])
        if vm.tag == CLIENT or vm.tag == LB:
            if "lxdbr1" in bridges:
                bridges_to_connect.append(bridges['lxdbr1'])
        for b in bridges_to_connect:
            bridges_handler.attach(vm.name, to_bridge=b)
            # Asiganamos una ip que no exista todavia
            existing_ips = []
            existing_vms = register.load(vms_handler.ID)
            for vm in existing_vms:
                existing_ips += vm.networks.values() 
            ip = f"{b.ipv4_addr[:-4]}{j+10}"
            if existing_vms != None:
                while ip in existing_ips:
                    j += 1 
                    ip = f"{b.ipv4_addr[:-4]}{j+10}"
            j += 1 
            vms_handler.connect(vm, with_ip=ip, to_network=b.ethernet)
        vms_handler.configure_netfile(vm)
        
def serialize_vms(*servers) -> list:
    if register.load(vms_handler.ID) != None: return []
    vms = []
    lb = VirtualMachine("lb", image, tag=LB)
    vms.append(lb)
    vms += serialize_servers(*servers)
    client = VirtualMachine("client", image, tag=CLIENT)
    vms.append(client)
    return vms

def serialize_servers(*servers):
    servs = []
    if len(servers) == 0: return []
    j = 1
    vms = objectlist_as_dict(register.load(vms_handler.ID), key_attribute="name")
    if type(servers[0]) == int:
        numServs = servers[0]
        for i in range(numServs):
            try:
                name = servers[i+1] 
            except:
                name = f"s{j}"
                if vms != None:
                    while name in vms:
                        j += 1   
                        name = f"s{j}"
                j += 1
            servs.append(VirtualMachine(name, image, tag=SERVER))
    else:
        for name in servers: 
            servs.append(VirtualMachine(name, image, tag=SERVER))
    return servs

def serialize_bridges(numBridges:int) -> list:
    if register.load(bridges_handler.ID) != None: return []
    bridges = []
    for i in range(numBridges):
        b_name = f"lxdbr{i}"
        b = Bridge(
            b_name, 
            ethernet=f"eth{i}",
            ipv4_nat=True, ipv4_addr=f"10.0.{i}.1/24"
        )
        bridges.append(b)
    return bridges

def update_conexions():
    bridges = register.load(register_id=bridges_handler.ID)
    if bridges == None: return
    
    vms = register.load(register_id=vms_handler.ID)
    if vms == None:
        names_existing_vms = []
    else:
        names_existing_vms = list(map(lambda vm: vm.name, vms))
    
    for b in bridges:
        deleted = []
        for vm_name in b.used_by:
            if vm_name not in names_existing_vms:
                deleted.append(vm_name)
        for d in deleted:
            b.used_by.remove(d)
    register.update(bridges_handler.ID, bridges)

def printProgramState():
    vms = register.load(register_id=vms_handler.ID)
    bridges = register.load(register_id=bridges_handler.ID)
    print("VIRTUAL MACHINES")
    if vms != None:
        for vm in vms:
            print(pretty(vm))
    else:
        print("No virtual machines created by the program")
    print("BRIDGES")
    if bridges != None:       
        for b in bridges:
            print(pretty(b))
    else:
        print("No bridges created by the program")