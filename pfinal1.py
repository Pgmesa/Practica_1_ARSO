# Integrantes del grupo: Pablo García Mesa, Fernando Fernandez Martín, Santiago González Gómez 
import sys
import logging
import bashHandler as bash
from CLInterface import cmdLineError
from config import config_logger
from bashCmds import cmd_logger

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
    except cmdLineError as clErr:
        main_logger.error(f" {clErr}")
    else:
        if args_processed == None: return
        configLogers(args_processed)
        main_logger.info(" Programa iniciado")
        bash.execute(args_processed)
        main_logger.info(" Programa finalizado")
        
def configLogers(args:list):
    if "-d" in args:
        logLvl = logging.DEBUG
    elif "-v" in args:
        logLvl = logging.INFO
    else:
        logLvl = logging.WARNING
    main_logger.setLevel(logLvl)
    cmd_logger.setLevel(logLvl)
    config_logger.setLevel(logLvl)
        
if __name__ == "__main__":
    main()
