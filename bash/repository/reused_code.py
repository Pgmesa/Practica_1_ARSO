
import logging

import program.controllers.containers as containers
import dependencies.register.register as register
from dependencies.utils.tools import objectlist_as_dict, remove_many

# --------------------------------------------------------------------
def target_containers(logger=None):
    if logging == None:
        logger = logging.getLogger(__name__)
    def _target_containers(cmd):
        def get_targets(*args, **kargs):
            cs = register.load(containers.ID)
            if cs == None:
                msg = " No existen contenedores creados por el programa"
                logger.error(msg)
                return
            # Comprobamos si hay que operar sobre todos los existentes 
            # o solo algunos en concreto
            names_given = list(args)
            c_dict = objectlist_as_dict(cs, "name")
            target_cs = cs
            if len(args) != 0: 
                valid_names = filter(lambda name: name in c_dict, names_given)
                target_cs = list(map(lambda valid: c_dict[valid], valid_names))
            # Notificamos los incorrectos. Eliminamos los nombres validos 
            # de los que nos han pasado y si siguen quedando nombres 
            # significa que no son validos. 
            remove_many(*c_dict.keys(), remove_in=names_given)
            for wrong in names_given:
                logger.error(f" No existe el contenedor '{wrong}' en este programa")
            # En caso de que haya algun contenedor valido
            if len(target_cs) != 0:
                cmd(*target_cs, **kargs)
        return get_targets
    return _target_containers

# --------------------------------------------------------------------