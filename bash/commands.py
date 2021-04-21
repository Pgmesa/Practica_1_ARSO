import logging
import subprocess
from utils.tools import objectlist_as_dict
from contextlib import suppress

from utils.tools import concat_array, remove_many
import register.register as register
import bash.controllers.containers as containers
import bash.controllers.bridges as bridges
import bash.controllers.program as program

cmd_logger = logging.getLogger(__name__)

def crear(*args, **flags):
    if register.load(bridges.ID) != None:
        cmd_logger.error(" La plataforma de servidores ya ha sido desplegada, " +
                                "se debe destruir la anterior para crear otra nueva")
        return
    # Eliminamos el nombre del agumento opcional (en caso de que este)
    args = list(args)
    with suppress(Exception):
        args.pop(1)
        
    cmd_logger.info(" Desplegando la plataforma de servidores...")
    
    # Creando contenedores
    cs = containers.serialize(*args)
    cmd_logger.debug(f" Nombre de contenedores serializados --> '{concat_array(*cs)}'")
    launch = True if "-l" in flags["flg"] else False
    show = True if not launch and "-q" not in flags["flg"] else False
    cmd_logger.debug(f" Launch --> {launch} | show --> {show}")
    cmd_logger.info(" Inicializando contenedores...\n")
    successful_cs = containers.init(*cs, show_list=show)
    cmd_logger.info(f" Succesful -> {concat_array(*successful_cs)} "
                        f"en registro con id '{containers.ID}'")
    # Creando bridges
    bgs = bridges.serialize(numBridges=2)
    cmd_logger.debug(f" Nombre de bridges serializados --> '{concat_array(*bgs)}'")
    cmd_logger.info(" Inicializando bridges...\n")
    bridges.init(*bgs)
    # Estableciendo conexiones
    cmd_logger.info(" Estableciendo conexiones entre contenedores y bridges...\n")
    program.connect_machines()
    cmd_logger.info(" Conexiones establecidas\n")
    
    # Arrancamos los contenedores creados con exito (si nos lo han pedido) 
    if successful_cs != None and launch:
        c_names = list(map(lambda c: c.name, successful_cs))
        arrancar(*c_names, **flags)        

def arrancar(*args, **flags):
    cs = register.load(containers.ID)
    if cs == None:
        cmd_logger.error(" No existen contenedores creados por el programa")
        return
    # Comprobamos si hay que arrancar todos los existentes o solo algunos en
    # concreto
    names_given = list(args)
    c_dict = objectlist_as_dict(cs, "name")
    target_cs = cs
    if len(args) != 0: 
        valid_names = filter(lambda name: name in c_dict, names_given)
        target_cs = list(map(lambda valid: c_dict[valid], valid_names))
    # Arrancamos los contenedores validos
    cmd_logger.info(f" Arrancando contenedores '{concat_array(*target_cs)}'...")
    containers.start(*target_cs)
    # Notificamos los incorrectos. Eliminamos los nombres validos de los 
    # que nos han pasado y si siguen quedando nombres significa que no son validos. 
    remove_many(*c_dict.keys(), remove_in=names_given)
    for wrong in names_given:
        cmd_logger.error(f" No existe el contenedor '{wrong}' en este programa")
    # Si nos lo indican, abrimos las terminales de los contenedores arrancados
    if "-t" in flags["flg"]:
        c_names = list(map(lambda c: c.name, target_cs))
        xterm(*c_names,**flags)

def parar(*args, **flags):
    cs = register.load(containers.ID)
    if cs == None:
        cmd_logger.error(" No existen contenedores creados por el programa")
        return
    # Comprobamos si hay que parar todos los existentes o solo algunos en
    # concreto
    names_given = list(args)
    c_dict = objectlist_as_dict(cs, "name")
    target_cs = cs
    if len(args) != 0: 
        valid_names = filter(lambda name: name in c_dict, names_given)
        target_cs = list(map(lambda valid: c_dict[valid], valid_names))
    # Paramos los contenedores validos
    cmd_logger.info(f" Deteniendo contenedores '{concat_array(*target_cs)}'...")
    containers.stop(*target_cs)
    # Notificamos los incorrectos. Eliminamos los nombres validos de los 
    # que nos han pasado y si siguen quedando nombres significa que no son validos. 
    remove_many(*c_dict.keys(), remove_in=names_given)
    for wrong in names_given:
        cmd_logger.error(f" No existe el contenedor '{wrong}' en este programa")
        
def pausar(*args, **flags):
    cs = register.load(containers.ID)
    if  cs == None:
        cmd_logger.error(" No existen contenedores creados por el programa")
        return
    # Comprobamos si hay que pausar todos los existentes o solo algunos en
    # concreto
    names_given = list(args)
    c_dict = objectlist_as_dict(cs, "name")
    target_cs = cs
    if len(args) != 0: 
        valid_names = filter(lambda name: name in c_dict, names_given)
        target_cs = list(map(lambda valid: c_dict[valid], valid_names))
    # Pausamos los contenedores validos
    cmd_logger.info(f" Pausando contenedores '{concat_array(*target_cs)}'...")
    containers.pause(*target_cs)
    # Notificamos los incorrectos. Eliminamos los nombres validos de los 
    # que nos han pasado y si siguen quedando nombres significa que no son validos. 
    remove_many(*c_dict.keys(), remove_in=names_given)
    for wrong in names_given:
        cmd_logger.error(f" No existe el contenedor '{wrong}' en este programa")

def añadir(*args, **flags):
    if register.load(bridges.ID) == None:
        cmd_logger.error(" La plataforma de servidores no ha sido desplegada, " +
                                "se debe crear una nueva antes de añadir los servidores")
    # Eliminamos el nombre del agumento opcional (en caso de que este)
    args = list(args)
    with suppress(Exception):
        args.pop(1)
    
    # Creando contenedores    
    cs = containers.serialize(*args)
    cmd_logger.debug(f" Nombre de contenedores serializados --> '{concat_array(*cs)}'")
    launch = True if "-l" in flags["flg"] else False
    show = True if not launch and "-q" not in flags["flg"] else False
    cmd_logger.debug(f" Launch --> {launch} | show --> {show}")
    cmd_logger.info(" Añadiendo contenedores...\n")
    successful_cs = containers.add(*cs, show_list=show)   
        
   # Estableciendo conexiones
    cmd_logger.info(" Estableciendo conexiones entre contenedores y bridges...\n")
    program.connect_machines()
    cmd_logger.info(" Conexiones establecidas\n")
    
    # Arrancamos los contenedores creados con exito (si nos lo han pedido) 
    if successful_cs != None and launch:
        c_names = list(map(lambda c: c.name, successful_cs))
        arrancar(*c_names, **flags)

def eliminar(*args, **flags):
    if not "-f" in flags["flg"]:
        print(f"Se eliminaran los servidores: '{concat_array(*args)}'")
        answer = str(input("¿Estas seguro?(y/n): "))
        if answer.lower() != "y":
            return
    cs = register.load(containers.ID)
    if cs == None:
        cmd_logger.error(" No existen contenedores creados por el programa")
        return
    # Comprobamos cuales hay que eliminar
    names_given = list(args)
    c_dict = objectlist_as_dict(cs, "name")
    valid_names = list(filter(lambda name: name in c_dict, names_given))
    target_cs = list(map(lambda valid: c_dict[valid], valid_names))
    # Eliminamos los existentes que nos hayan indicado
    cmd_logger.info(f" Eliminando contenedores '{concat_array(*target_cs)}'...\n")
    successful = containers.delete(*target_cs)
    if len(successful) == len(cs):
        register.remove(register_id=containers.ID)
    else:
        not_deleted = []
        for c in c_dict.values():
            if c not in successful:
                not_deleted.append(c)
        register.update(containers.ID, not_deleted)
    # Notificamos los incorrectos. Eliminamos los nombres validos de los 
    # que nos han pasado y si siguen quedando nombres significa que no son validos. 
    remove_many(*c_dict.keys(), remove_in=names_given)
    for wrong in names_given:
        cmd_logger.error(f" No existe el contenedor '{wrong}' en este programa")
    # Actualizamos los contenedores que estan asociados a cada bridge
    program.update_conexions()
        

def destruir(*args, **flags):
    if not "-f" in flags["flg"]:
        print("Se borrara por completo la infraestructura creada, " + 
                "contenedores, bridges y sus conexiones aun podiendo estar arrancadas")
        answer = str(input("¿Estas seguro?(y/n): "))
        if answer.lower() != "y":
            return
    if register.load(bridges.ID) == None:
        cmd_logger.error(" La plataforma de servidores no ha sido desplegada, " +
                                "se debe crear una nueva antes de poder destruir")
        return
    # Eliminamos contenedores 
    cs = register.load(containers.ID)
    if cs == None:
        cmd_logger.warning(" No existen servidores en el programa")
    else:
        c_names = list(map(lambda c: c.name, cs))
        eliminar(*c_names, flg=["-f"])
    # Eliminamos bridges
    bgs = register.load(bridges.ID)
    cmd_logger.info(" Eliminando bridges...\n")
    successful_bgs = bridges.delete(*bgs)
    # Eliminamos el registro
    if len(successful_bgs) == len(bgs):
        register.remove()
    # Guardamos los que no se hayan eliminado bien
    else:
        b_dict = objectlist_as_dict(bgs, "name")
        not_deleted = []
        for b in b_dict.values():
            if b not in successful_bgs:
                not_deleted.append(b)
        register.update(bridges.ID, not_deleted)
            
    
def show(*args, **flags):
    if args[0] == "diagram":
        program.show_diagram()
    elif args[0] == "state":
        program.print_state()

def xterm(*args, **flags):
    cs = register.load(containers.ID)
    if cs == None:
        cmd_logger.error(" No existen contenedores creados por el programa")
        return
    # Comprobamos si hay que arrancar todos los existentes o solo alunos en
    # concreto
    names_given = list(args)
    c_dict = objectlist_as_dict(cs, "name")
    if len(args) != 0: 
        valid_names = filter(lambda name: name in c_dict, names_given)
        cs = list(map(lambda valid: c_dict[valid], valid_names))
    # Abrimos las terminales de los contenedores validos
    for c in cs: c.open_terminal()
    # Notificamos los incorrectos. Eliminamos los nombres validos de los 
    # que nos han pasado y si siguen quedando nombres significa que no son validos. 
    remove_many(*c_dict.keys(), remove_in=names_given)
    for wrong in names_given:
        cmd_logger.error(f" No existe el contenedor '{wrong}' en este programa")