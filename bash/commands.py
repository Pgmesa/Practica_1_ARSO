
import subprocess

import bash.manager as manager
import controllers.vms_handler as vms_handler
import controllers.bridges_handler as bridges_handler


def crear(*args, **flags):
    vms = manager.serializeVms(*args)
    vms_handler.initVms(vms)
    bridges = manager.serializeBridges(numBridges=2)
    bridges_handler.initBridges(bridges)
    manager.connect_machines()
            

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
    vms_handler.deleteVms()
    manager.update_conexions()
    bridges_handler.deleteBridges()

def pausar(*args, **flags):
    vms_handler.pauseVms(*args)

def lanzar(*args, **flags):
    crear(*args, **flags)
    arrancar(*args[1:], **flags)

def añadir(*args, **flags):
    print(args, flags)

def eliminar(*args, **flags):
    if not "-f" in flags["flg"]:
        print("Se eliminaran los servidores: '", *args, "'")
        answer = str(input("¿Estas seguro?(y/n): "))
        if answer.lower() != "y":
            return
    vms_handler.deleteVms(*args)
    manager.update_conexions()
    
def show(*args, **flags):
    if args[0] == "diagram":
        subprocess.Popen(
            ["display", "bash/images/diagram.png"],
            stdout=subprocess.PIPE
        ) 
    elif args[0] == "state":
        manager.printProgramState()

def xterm(*args, **flags):
    vms_handler.open_vms_terminal(*args)