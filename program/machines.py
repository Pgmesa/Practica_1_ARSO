
import program.controllers.bridges as bridges
import program.controllers.containers as containers
import dependencies.register.register as register
from dependencies.lxc_classes.container import Container
from dependencies.lxc_classes.bridge import Bridge
from dependencies.utils.tools import objectlist_as_dict

# --------------------------------------------------------------------
# Tags of the containers available in this program
SERVER = "server"; LB = "load balancer"; CLIENT  = "client"

default_image = "ubuntu:18.04"

def get_loadbalancer(image=default_image) -> Container:
    return Container("lb", image, tag=LB)

def get_clients(image=default_image) -> Container:
    return Container("cl", image, tag=CLIENT)

def serialize_servers(num, *names, image=default_image) -> list:
    servs = []
    server_names = process_names(containers.ID, num, *names)
    for name in server_names:
        servs.append(Container(name, image, tag=SERVER))
    return servs

def serialize_bridges(numBridges:int) -> list:
    bgs = []
    for i in range(numBridges):
        b_name = f"lxdbr{i}"
        b = Bridge(
            b_name, 
            ethernet=f"eth{i}",
            ipv4_nat=True, ipv4_addr=f"10.0.{i}.1/24"
        )
        bgs.append(b)
    return bgs

def process_names(register_id, num, *names) -> list:
    server_names = []
    j = 1
    machine_names = objectlist_as_dict(
        register.load(register_id), 
        key_attribute="name"
    )
    if machine_names == None:
        machine_names = []
    for i in range(num):
        try:
            name = names[i] 
        except:
            # Si no nos han proporcionado mas nombres, buscamos
            # uno que no exista ya o no nos hayan pasado antes
            name = f"s{j}"
            j += 1
            while (name in server_names or 
                     name in machine_names):   
                name = f"s{j}"
                j += 1
        server_names.append(name)
    return server_names
# --------------------------------------------------------------------