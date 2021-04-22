# Integrantes del grupo: Pablo García Mesa, Santiago González Gómez, Fernando Fernández Martín
import sys
import logging

import bash.bash_handler as bash
from dependencies.cli.aux_classes import CmdLineError
    
# -------------------------- MAIN (BEGGINING OF EXECUTION)--------------------------
# ----------------------------------------------------------------------------------
# This main file just defines the execution flow the program will follow

logging.basicConfig(level=logging.NOTSET)
main_logger = logging.getLogger(__name__)

def main():
    cli = bash.config_cli()
    try:
        args_processed, flags = cli.process_cmdline(sys.argv)
        if args_processed == None and "-h" in flags: return
    except CmdLineError as clErr:
        main_logger.error(f" {clErr}")
    else:
        bash.config_verbosity(flags)
        main_logger.info(" Programa iniciado")
        try:
            bash.execute(args_processed, flags)
        except KeyboardInterrupt:
            main_logger.warning(" Programa interrumpido")
        except Exception as err:
            main_logger.error(" Error inesperado en el programa (no controlado)")
            answer = input("¿Obtener traza completa?(y/n): ")
            if answer.lower() == "y":
                main_logger.exception(err)
        main_logger.info(" Programa finalizado")  
        
if __name__ == "__main__":
    main()
