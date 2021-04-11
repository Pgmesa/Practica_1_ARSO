# Integrantes del grupo: Pablo García Mesa, Santiago González Gómez, Fernando Fernández Martín
import sys
import logging
import bash_handler as bash
from cli.aux_classes import CmdLineError
from vms.controllers import ctrl_logger as vm_logger
from bridges.controllers import ctrl_logger as br_logger

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
    vm_logger.setLevel(logLvl)
    br_logger.setLevel(logLvl)
        
if __name__ == "__main__":
    main()
