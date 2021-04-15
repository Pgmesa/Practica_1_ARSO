# Integrantes del grupo: Pablo García Mesa, Santiago González Gómez, Fernando Fernández Martín
import sys
import logging
import bash_handler as bash

from cli.aux_classes import CmdLineError

logging.basicConfig(level=logging.NOTSET)
main_logger = logging.getLogger(__name__)
    
# -------------------------- MAIN (BEGGINING OF EXECUTION)--------------------------
# ----------------------------------------------------------------------------------
# This main file just defines the execution flow the program will follow

def main():
    cli = bash.configCli()
    args = sys.argv
    try:
        args_processed = cli.processCmdline(args)
    except CmdLineError as clErr:
        main_logger.error(f" {clErr}")
    else:
        if args_processed == None: return
        bash.configVerbosity(args_processed)
        main_logger.info(" Programa iniciado")
        try:
            bash.execute(args_processed)
        except Exception as err:
            main_logger.error(" Error inesperado en el programa (no controlado)")
            answer = input("¿Obtener traza completa?(y/n): ")
            if answer.lower() == "y":
                main_logger.exception(err)
        main_logger.info(" Programa finalizado")  
        
if __name__ == "__main__":
    main()
