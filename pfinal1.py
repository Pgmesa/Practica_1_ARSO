# Integrantes del grupo: Pablo García Mesa, Santiago González Gómez, Fernando Fernández Martín
import sys
import logging
import subprocess

import bash.bash_handler as bash
from bash.bash_handler import CmdLineError
import program.functions as program
from program.functions import ProgramError
 
# ------------------- MAIN (INICIO DE EJECUCION) ---------------------
# --------------------------------------------------------------------
# Este es un fichero fachada en el cual se ve de forma global el 
# flujo de ejecucion que sigue el programa sin entrar en detalles

logging.basicConfig(level=logging.NOTSET)
main_logger = logging.getLogger(__name__)
# --------------------------------------------------------------------
def main():
    cli = bash.config_cli()
    try:
        # Procesamos la linea de comandos (CmdLineError)
        args_processed = cli.process_cmdline(sys.argv)
        if args_processed == None: return
        # Configuramos la cantidad de info que se va a mostar
        bash.config_verbosity(args_processed["flags"])
        # Iniciamos el programa
        main_logger.info(" Programa iniciado")
        # Realizamos unas comprobaciones previas (ProgramError)
        program.check_enviroment()
        program.check_updates()
        # Ejecutamos la orden
        main_logger.debug(f" Ejecutando la orden {args_processed}")
        bash.execute(args_processed)
    # Manejamos los errores que puedan surgir 
    except CmdLineError as clErr:
        main_logger.error(f" {clErr}")
    except KeyboardInterrupt:
        main_logger.warning(" Programa interrumpido")
    except ProgramError as err:
        main_logger.critical(err)
    except Exception as err:
        err_msg = " Error inesperado en el programa (no controlado)"
        main_logger.critical(err_msg)
        answer = input("¿Obtener traza completa?(y/n): ")
        if answer.lower() == "y":
            main_logger.exception(err)
    finally:
        main_logger.info(" Programa finalizado")
        
if __name__ == "__main__":
    main()
# --------------------------------------------------------------------
