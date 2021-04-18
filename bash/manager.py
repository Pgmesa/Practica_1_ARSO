
from os import path

from utils.tools import pretty
import register.register as register
from wrapper_classes.bridge import Bridge
from wrapper_classes.vm import VirtualMachine
import controllers.vms as vms_handler
import controllers.bridges as bridges_handler


# Tags of the Machines available in this program
SERVER = "server"
LB = "load balancer"
CLIENT  = "client"


def connect_machines(vms:list, bridges:dict):
    for i, vm in enumerate(vms):
        bridges_to_connect = []
        if vm.tag == SERVER or vm.tag == LB:
            if "lxdbr0" in bridges:
                bridges_to_connect.append(bridges['lxdbr0'])
        if vm.tag == CLIENT or vm.tag == LB:
            if "lxdbr1" in bridges:
                bridges_to_connect.append(bridges['lxdbr1'])
        for b in bridges_to_connect:
            bridges_handler.attach(vm.name, to_bridge=b)
            vms_handler.connect(vm, with_ip=f"{b.ipv4_addr[:-4]}{i+10}", to_network=b.ethernet)
        vms_handler.configure_netfile(vm)
        
def serializeVms(numServs) -> list:
    if path.isfile("vms_register"):
        return []
    vms = []
    image = "ubuntu1804"
    lb = VirtualMachine("lb", image, tag=LB)
    vms.append(lb)
    for i in range(numServs): 
        vms.append(VirtualMachine(f"s{i+1}", image, tag=SERVER))
    client = VirtualMachine("client", image, tag=CLIENT)
    vms.append(client)
    return vms

def serializeBridges(numBridges) -> dict:
    if path.isfile("bridges_register"):
        return {}
    bridges = {}
    for i in range(numBridges):
        b_name = f"lxdbr{i}"
        b = Bridge(
            b_name, 
            ethernet=f"eth{i}",
            ipv4_nat=True, ipv4_addr=f"10.0.{i}.1/24"
        )
        bridges[b_name] = b
    return bridges

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