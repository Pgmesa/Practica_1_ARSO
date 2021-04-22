
import dependencies.register.register as register
import program.controllers.bridges as bridges
import program.controllers.containers as containers
from dependencies.utils.tools import pretty, objectlist_as_dict
from dependencies.lxc_classes.container import Container
from dependencies.lxc_classes.bridge import Bridge

# --------------------------------------------------------------------
# Tags of the containers available in this program
SERVER = "server"; LB = "load balancer"; CLIENT  = "client"

# Imagen a utilizar
image = "ubuntu1804"

def serialize_containers(*servers, servs=True) -> list:
    lb = Container("lb", image, tag=LB)
    client = Container("client", image, tag=CLIENT)
    cs = [lb, client]
    if servs:
        cs += serialize_servers(*servers)
    return cs

def serialize_servers(*servers):
    servs = []
    server_names = process_names(containers.ID, *servers)
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

def process_names(register_id, *servers):
    server_names = []
    if len(servers) == 0: return []
    j = 1
    machine_names = objectlist_as_dict(
        register.load(register_id), 
        key_attribute="name"
    )
    if type(servers[0]) == int:
        numServs = servers[0]
        for i in range(numServs):
            try:
                name = servers[i+1] 
            except:
                # Si no nos han proporcionado nombre, 
                # buscamos uno que no exista ya
                name = f"s{j}"
                if machine_names != None:
                    while name in machine_names:
                        j += 1   
                        name = f"s{j}"
                j += 1
            server_names.append(name)
    else:
        for name in servers: 
            server_names.append(name)
    return server_names
# --------------------------------------------------------------------