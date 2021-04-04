# Integrantes del grupo: Pablo García Mesa, Fernando Fernandez Martín, Santiago González Gómez 
import sys
import logging
import bashHandler as bash
from bashHandler import cmdLineError

logging.basicConfig(level=logging.NOTSET)
main_logger = logging.getLogger(__name__)

# -------------------------- MAIN (BEGGINING OF EXECUTION)--------------------------
# ----------------------------------------------------------------------------------
# This main file just defines the execution flow the program will follow

def main():
    args = sys.argv
    try:
        args_processed = bash.processCmdline(args)
    except cmdLineError as clErr:
        main_logger.error(f" {clErr}")
    else:
        if args_processed == None:
            return
        main_logger.setLevel(bash.logLvl)
        main_logger.info(" Programa iniciado")
        bash.execute(args_processed)
        main_logger.info(" Programa finalizado")
        
if __name__ == "__main__":
    main()
