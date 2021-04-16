
import subprocess

import execution.manager as manager
import controllers.vms as vms_handler
import controllers.bridges as bridges_handler


def crear(*args):
    vms = manager.serializeVms(numServs=args[0])
    successful_vms = vms_handler.initVms(vms)
    if successful_vms != None:
        bridges = manager.serializeBridges(numBridges=2)
        succesful_brdgs = bridges_handler.initBridges(bridges.values())
        manager.connect_machines(vms=successful_vms, bridges=succesful_brdgs)
            

def arrancar(*args):
    vms_handler.startVms()
    if "-t" in args:
        vms_handler.open_vms_terminal()

def parar(*args):
    vms_handler.stopVms()

def destruir(*args):
    if not "-f" in args:
        print("Se borraran las maquinas virtuales, bridges" + 
                                " y sus conexiones aun podiendo estar arrancadas")
        answer = str(input("¿Estas seguro?(y/n): "))
        if answer.lower() != "y":
            return
    outcome = vms_handler.deleteVms()
    if outcome != -1:
        bridges_handler.deleteBridges()

def pausar(*args):
    vms_handler.pauseVms()

def lanzar(*args):
    crear(*args)
    arrancar(*args)

def añadir(*args):
    print(args)

def eliminar(*args):
    print(args)
    
def show(*args):
    if args[0] == "diagram":
        subprocess.Popen(
            ["display", "execution/images/diagram.png"],
            stdout=subprocess.PIPE
        ) 
    elif args[0] == "state":
        manager.printProgramState()

def xterm(*args):
    vms_handler.open_vms_terminal(vm_name=args[0])