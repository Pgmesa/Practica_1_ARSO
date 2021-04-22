
import logging
from contextlib import suppress

import program.controllers.bridges as bridges
import program.controllers.containers as containers
import program.machines as machines
import program.functions as program
import dependencies.register.register as register
from dependencies.utils.tools import objectlist_as_dict
from dependencies.utils.tools import concat_array, remove_many
from .reused_code import target_containers


cmd_logger = logging.getLogger(__name__)
# --------------------------------------------------------------------
@target_containers(cmd_logger)           
def arrancar(*target_cs, **flags):
    # Arrancamos los contenedores validos
    msg = f" Arrancando contenedores '{concat_array(target_cs)}'..."
    cmd_logger.info(msg)
    succesful_cs = containers.start(*target_cs)
    if not "-q" in flags["flg"]:
        program.lxc_list()
    cs_s = concat_array(succesful_cs)
    msg = (f" Los contenedores '{cs_s}' han sido arrancados \n")
    cmd_logger.info(msg)
    # Si nos lo indican, abrimos las terminales de los contenedores 
    # arrancados
    if "-t" in flags["flg"]:
        c_names = list(map(lambda c: c.name, target_cs))
        xterm(*c_names,**flags)
        
# --------------------------------------------------------------------
@target_containers(cmd_logger) 
def parar(*target_cs, **flags):
    # Paramos los contenedores validos
    msg = f" Deteniendo contenedores '{concat_array(target_cs)}'..."
    cmd_logger.info(msg)
    succesful_cs = containers.stop(*target_cs)
    if not "-q" in flags["flg"]:
        program.lxc_list()
    cs_s = concat_array(succesful_cs)
    msg = (f" Los contenedores '{cs_s}' han sido detenidos \n")
    cmd_logger.info(msg)
        
# --------------------------------------------------------------------  
@target_containers(cmd_logger)  
def pausar(*target_cs, **flags):
    # Pausamos los contenedores validos
    msg = f" Parando contenedores '{concat_array(target_cs)}'..."
    cmd_logger.info(msg)
    succesful_cs = containers.pause(*target_cs)
    if not "-q" in flags["flg"]:
        program.lxc_list()
    cs_s = concat_array(succesful_cs)
    msg = (f" Los contenedores '{cs_s}' han sido pausados \n")
    cmd_logger.info(msg)

# --------------------------------------------------------------------
@target_containers(cmd_logger) 
def eliminar(*target_cs, **flags):
    if not "-f" in flags["flg"]:
        print("Se eliminaran los servidores:" +
                    f" '{concat_array(target_cs)}'")
        answer = str(input("¿Estas seguro?(y/n): "))
        if answer.lower() != "y":
            return
    # Eliminamos los existentes que nos hayan indicado
    msg = f" Eliminando contenedores '{concat_array(target_cs)}'..."
    cmd_logger.info(msg)
    succesful_cs = containers.delete(*target_cs)
    # Actualizamos los contenedores que estan asociados a cada bridge
    program.update_conexions()
    if not "-q" in flags["flg"]:
        program.lxc_list()
    cs_s = concat_array(succesful_cs)
    msg = (f" Los contenedores '{cs_s}' han sido eliminados \n")
    cmd_logger.info(msg)

# --------------------------------------------------------------------
@target_containers(cmd_logger) 
def xterm(*target_cs, **flags):
    # Arrancamos los contenedores validos
    cs_s = concat_array(target_cs)
    msg = f" Abriendo terminales de contenedores '{cs_s}'..."
    cmd_logger.info(msg)
    succesful_cs = containers.open_terminal(*target_cs)
    cs_s = concat_array(succesful_cs)
    msg = f" Se ha abierto la terminal de los contenedores '{cs_s}'\n"
    cmd_logger.info(msg)
# --------------------------------------------------------------------
def crear(*args, **flags):
    if register.load(bridges.ID) != None:
        msg = (" La plataforma de servidores ya ha sido desplegada, " 
              + "se debe destruir la anterior para crear otra nueva")
        cmd_logger.error(msg)
        return   
    cmd_logger.info(" Desplegando la plataforma de servidores...\n")
    # Creando bridges
    bgs = machines.serialize_bridges(numBridges=2)
    bgs_s = concat_array(bgs)
    cmd_logger.debug(f" Nombre de bridges serializado --> '{bgs_s}'")
    cmd_logger.info(" Creando bridges...")
    succesful_bgs = bridges.init(*bgs)
    if not "-q" in flags["flg"]:
        program.lxc_network_list()
    bgs_s = concat_array(succesful_bgs)
    cmd_logger.info(f" Bridges '{bgs_s}' creados\n")
    # Creando contenedores
    extra = machines.serialize_containers(servs=False)
    añadir(*args, **flags, extra_cs=extra) 
    cmd_logger.info(" Plataforma de servidores desplegada")

# --------------------------------------------------------------------
def añadir(*args, extra_cs:list=[], **flags):
    if register.load(bridges.ID) == None:
        msg = (" La plataforma de servidores no ha sido  " +
                    "desplegada, se debe crear una nueva antes " +
                        "de añadir los servidores")
        cmd_logger.error(msg)
        return
    # Eliminamos el nombre del agumento opcional (en caso de que este)
    args = list(args)
    with suppress(Exception):
        args.pop(1)
    # Creando contenedores    
    cs = machines.serialize_servers(*args) + extra_cs
    cs_s = concat_array(cs)
    msg = f" Nombre de contenedores serializados --> '{cs_s}'"
    cmd_logger.debug(msg)
    launch = True if "-l" in flags["flg"] else False
    show = True if not launch and "-q" not in flags["flg"] else False
    cmd_logger.debug(f" Launch --> {launch} | show --> {show}")
    cmd_logger.info(f" Inicializando contenedores '{cs_s}'...")
    successful_cs = containers.init(*cs)
    if not "-q" in flags["flg"]:
        program.lxc_list() 
    cs_s = concat_array(successful_cs)
    msg = (f" Cotenedores '{cs_s}' inicializados\n")
    cmd_logger.info(msg)
    if len(successful_cs) != 0:     
        # Estableciendo conexiones
        cmd_logger.info(" Estableciendo conexiones " +
                                "entre contenedores y bridges...")
        program.connect_machines()
        cmd_logger.info(" Conexiones establecidas\n")
        # Arrancamos los contenedores creados con exito 
        # (si nos lo han pedido) 
        if successful_cs != None and launch:
            c_names = list(map(lambda c: c.name, successful_cs))
            arrancar(*c_names, **flags) 
                 
# --------------------------------------------------------------------
def destruir(*args, **flags):
    if not "-f" in flags["flg"]:
        msg = ("Se borrara por completo la infraestructura " + 
                "creada, contenedores, bridges y sus conexiones " + 
                    "aun podiendo estar arrancadas")
        print(msg)
        answer = str(input("¿Estas seguro?(y/n): "))
        if answer.lower() != "y":
            return
    if register.load(bridges.ID) == None:
        msg = (" La plataforma de servidores no ha sido desplegada, " 
                 + "se debe crear una nueva antes de poder destruir")
        cmd_logger.error(msg)
        return
    cmd_logger.info(" Destruyendo plataforma...\n")
    # Eliminamos contenedores
    cs = register.load(containers.ID)
    if cs == None:
        cmd_logger.warning(" No existen servidores en el programa")
    else:
        c_names = list(map(lambda c: c.name, cs))
        flags["flg"] = (*flags["flg"],"-f") # Añadimos el flag -f
        eliminar(*c_names, **flags)
    # Eliminamos bridges
    bgs = register.load(bridges.ID)
    if bgs == None: 
        cmd_logger.warning(" No existen bridges en el programa")
    else:
        msg = f" Eliminando bridges '{concat_array(bgs)}'..."
        cmd_logger.info(msg)
        successful_bgs = bridges.delete(*bgs)
        if not "-q" in flags["flg"]:
            program.lxc_network_list()
        bgs_s = concat_array(successful_bgs)
        msg = (f" Bridges '{bgs_s}' eliminados\n")
        cmd_logger.info(msg)  
    # Si se ha elimando todo eliminamos el registro   
    cs = register.load(containers.ID)
    bgs = register.load(bridges.ID) 
    if cs == None and bgs == None:
        register.remove()
        cmd_logger.info(" Plataforma destruida")
    else:
        msg = (" Plataforma destruida parcialmente " +
                        "(se han encontrado dificultades)") 
        cmd_logger.error(msg)
            
# --------------------------------------------------------------------   
def show(*args, **flags):
    if args[0] == "diagram":
        program.show_diagram()
    elif args[0] == "state":
        program.print_state()
        
# --------------------------------------------------------------------