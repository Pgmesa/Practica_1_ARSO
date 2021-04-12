import logging
import subprocess
from os import path
from contextlib import suppress

from cli.cli import Cli
from vms.vm import VirtualMachine
from bridges.bridge import Bridge
from tools import printProgramState
import vms.controllers as vms_handler
import bridges.controllers as bridges_handler

# -------------------------------BASH HANDLER-------------------------------
# --------------------------------------------------------------------------
# Defines how the program works and how the command line is going to be read
# and interpreted. The bashCmd module is not coupled with this one, they are
# independent.

# Tags of the Machines available in this program
SERVER = "server"
LB = "load balancer"
CLIENT  = "client"

def execute(args:list):
    """Executes the commands of the program'"""
    order = args[0]
    if order == "crear":
        vms = serializeVms(numServs=args[1])
        vms_handler.initVms(vms)
        bridges = serializeBridges(numBridges=2)
        bridges_handler.initBridges(bridges.values())
        connect_machines(vms=vms, bridges=bridges)
    elif order == "arrancar":
        vms_handler.startVms()
    elif order == "parar":
        vms_handler.stopVms()
    elif order == "destruir":
        if not "-f" in args:
            print("Se borraran las maquinas virtuales, bridges" + 
                                    " y sus conexiones aun podiendo estar arrancadas")
            response = str(input("¿Estas seguro?(y/n): "))
            if response.lower() != "y":
                return
        vms_handler.deleteVms()
        bridges_handler.deleteBridges()
    elif order == "añadir":
        print(args)
    elif order == "eliminar":
        print(args)
    elif order == "show":
        if args[1] == "diagram":
            subprocess.Popen(
                ["display", "images/diagram.png"],
                stdout=subprocess.PIPE
            ) 
        elif args[1] == "state":
            printProgramState()
    
def connect_machines(vms:list, bridges:dict):
    for i, vm in enumerate(vms):
        if vm.tag == SERVER:
            bridges_to_connect = [bridges["lxdbr0"]]
        elif vm.tag == LB:
            bridges_to_connect = [bridges["lxdbr0"], bridges["lxdbr1"]]
        else:
            bridges_to_connect = [bridges["lxdbr1"]]   
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
    # client = VirtualMachine("client", image, tag=CLIENT)
    # vms.append(client)
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

def applyVerbosity(args:list):
    if "-d" in args:
        logLvl = logging.DEBUG
        args.remove("-d")
    elif "-v" in args:
        logLvl = logging.INFO
        args.remove("-v")
    elif "-q" in args:
        logLvl = logging.ERROR
        args.remove("-q")
    else:
        logLvl = logging.WARNING
    root_logger = logging.getLogger()
    root_logger.setLevel(logLvl) 

def configCli() -> Cli:
    cli = Cli()
    # Arguments
    msg = ("<void or integer between(1-5)> --> " + 
            " creates and configures the number of servers especified\n " +
            "          (if void, 2 servers are created). It also initializes a load balancer" + 
            " and connects all vms with bridges")
    cli.addArg("crear", description=msg, extraArg=True, choices=[1,2,3,4,5], default=2)
    msg = "runs all the virtual machines already created"
    cli.addArg("arrancar", description=msg)
    msg = "stops the virtual machines currently running"
    cli.addArg("parar", description=msg)
    msg = "deletes every virtual machine created and all connections betweeen them"
    cli.addArg("destruir", description=msg)
    # Other functionalities
    msg = "<integer between(1-4)> adds the number of servers specified (the program can't surpass 5 servers)"
    cli.addArg("añadir", description=msg, extraArg=True, choices=[1,2,3,4])
    msg = "<name of the server> deletes the server specified"
    cli.addArg("eliminar", description=msg, extraArg=True)
    msg ="<diagram or state> shows information about the pupose of the program and it's current state"
    cli.addArg("show", description=msg, extraArg=True, choices=["diagram", "state"])
    
    #Options
    msg = "shows information about every process that is being executed"
    cli.addOption("-v", notCompatibleWith=["-d"], description=msg)
    msg = "option for debugging"
    cli.addOption("-d", notCompatibleWith=["-v"], description=msg)
    msg = "'quiet mode', doesn't show any msg during execution (only when an error occurs)"
    cli.addOption("-q", notCompatibleWith=["-v","-d"], description=msg)
    msg = "executes the action without asking confirmation"
    cli.addOption("-f", description=msg)
    return cli
