
import subprocess

import bash.manager as manager
import controllers.vms as vms_handler
import controllers.bridges as bridges_handler


def crear(*args, **flags):
    vms = manager.serializeVms(numServs=args[0])
    successful_vms = vms_handler.initVms(vms)
    if successful_vms != None:
        bridges = manager.serializeBridges(numBridges=2)
        succesful_brdgs = bridges_handler.initBridges(bridges.values())
        manager.connect_machines(vms=successful_vms, bridges=succesful_brdgs)
            

def arrancar(*args, **flags):
    vms_handler.startVms(*args)
    if "-t" in flags["flg"]:
        vms_handler.open_vms_terminal(*args)

def parar(*args, **flags):
    vms_handler.stopVms(*args)

def destruir(*args, **flags):
    if not "-f" in flags["flg"]:
        print("Se borraran las maquinas virtuales, bridges" + 
                                " y sus conexiones aun podiendo estar arrancadas")
        answer = str(input("¿Estas seguro?(y/n): "))
        if answer.lower() != "y":
            return
    outcome = vms_handler.deleteVms()
    if outcome != -1:
        bridges_handler.deleteBridges()

def pausar(*args, **flags):
    vms_handler.pauseVms(*args)

def lanzar(*args, **flags):
    crear(*args, **flags)
    arrancar(*args[1:], **flags)

def añadir(*args, **flags):
    print(args, flags)

def eliminar(*args, **flags):
    print(args, flags)
    
def show(*args, **flags):
    if args[0] == "diagram":
        subprocess.Popen(
            ["display", "execution/images/diagram.png"],
            stdout=subprocess.PIPE
        ) 
    elif args[0] == "state":
        manager.printProgramState()

def xterm(*args, **flags):
    vms_handler.open_vms_terminal(*args)