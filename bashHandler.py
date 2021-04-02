from tools import isPositiveInt, numInBetween
from bashCmds import createVms, startVms, stopVms, deleteVms, cmd_logger

# -------------------------------BASH HANDLER-------------------------------
# --------------------------------------------------------------------------
# Defines how the program works and how the command line is going to be read
# and interpreted. The bashCmd module is not coupled with this one, they are
# independent.

class cmdLineError(Exception):
    def __init__(self, msg:str):
        hlpm = "\nIntroduce el parametro -h para acceder a la ayuda"
        super().__init__(msg + hlpm)

def execute(args:list):
    """Executes the command line order 'crear', 'arrancar', 'parar' or 'destruir'"""
    order = args[0]
    if order == "crear":
        if len(args) == 1:
            createVms()
        else:
            createVms(numServs=args[1])
    elif order == "arrancar":
        startVms()
    elif order == "parar":
        stopVms()
    elif order == "destruir":
        deleteVms()

def processCmdline(args:list) -> list:
    """Checks if the arguments passed through the console are correct for this program.
    Executes the optional arguments found and returns the args filtered without them.
    If -h is found None is returned to indicate that nothing should be done outside this function"""
    args.pop(0)
    if "-h" in args:
        printHelp()
        return None
    if "-v" in args:
        cmd_logger.setLevel(20) # == logging.INFO
        args.remove("-v")
    else:
        cmd_logger.setLevel(30) # == logging.WARNING
    if len(args) == 1:
        order = args[0]
        valid_orders = ["crear", "arrancar", "parar", "destruir"]
        if order in valid_orders:
            return args
        else:
            msg = f" La orden '{order}' no es valida (ordenes validas: crear, arrancar, parar, destruir)"
            raise cmdLineError(msg)
    elif len(args) == 2:
        order = args[0]
        if order == "crear":
            if isPositiveInt(args[1]) and numInBetween(int(args[1]), [1,5]):
                args[1] = int(args[1])
                return args
            else:
                msg = f" El parametro '{args[1]}' no es valido, debe ser un entero positivo entre (1-5)"
                raise cmdLineError(msg)
        else:
            msg = f" La orden '{order}' no admite el parametro '{args[1]}'"
            raise cmdLineError(msg)
    else:
        msg = f" El numero de argumentos introducido en el programa es incorrecto"
        raise cmdLineError(msg)

def printHelp():
    """Shows information in console about the parameters that pfinal1.py admits"""
    print()
    print(" -- HELP --")
    print(" + pyhton3 pfinal1.py <orden> :")
    print("     -> crear <void or integer between(1-5)> -->" + 
                        " creates and configures the number of servers especified\n " +
                        "          (if void, 2 servers are created). It also initializes a load balancer.")
    print("     -> arrancar --> runs all the virtual machines already created")
    print("     -> parar --> stops the virtual machines currently running")
    print("     -> destruir --> deletes every virtual machine created and all connections betweeen them")
    print()
    print("     + Optional arguments: ")
    print("         -> -h --> help: shows the commands and optional arguments" +
                                " that this program can recieve")
    print("         -> -v --> verbosity: shows information about every process" +
                                " that is being executed")
    print()