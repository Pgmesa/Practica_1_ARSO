# Integrantes del grupo: Pablo García Mesa, Santiago González Gómez, Fernando Fernández Martín
import sys
import logging

import bash.bash_handler as bash
from dependencies.cli.aux_classes import CmdLineError
    
# ----------------- MAIN (BEGGINING OF EXECUTION) --------------------
# --------------------------------------------------------------------
# This main file just defines the execution flow of the program

logging.basicConfig(level=logging.NOTSET)
main_logger = logging.getLogger(__name__)
# --------------------------------------------------------------------
def main():
    cli = bash.config_cli()
    try:
        args_processed = cli.process_cmdline(sys.argv)
        if args_processed == None: return
    except CmdLineError as clErr:
        main_logger.error(f" {clErr}")
    else:
        bash.config_verbosity(args_processed["flags"])
        main_logger.info(" Programa iniciado")
        try:
            bash.execute(args_processed)
        except KeyboardInterrupt:
            main_logger.warning(" Programa interrumpido")
        except Exception as err:
            err_msg = " Error inesperado en el programa (no controlado)"
            main_logger.error(err_msg)
            answer = input("¿Obtener traza completa?(y/n): ")
            if answer.lower() == "y":
                main_logger.exception(err)
        main_logger.info(" Programa finalizado")  
        
if __name__ == "__main__":
    main()
# --------------------------------------------------------------------