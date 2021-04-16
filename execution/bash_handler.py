import logging

from cli.cli import Cli
from utils.decorators import timer
import execution.commands as repository

# -------------------------------BASH HANDLER-------------------------------
# --------------------------------------------------------------------------
# Defines how the program works and how the command line is going to be read
# and interpreted. The bashCmd module is not coupled with this one, they are
# independent.

commands = {}

@timer
def execute(args:list):
    """Executes the commands of the program'"""
    order = args[0]
    command = commands[order]
    args.pop(0)
    command(*args)
        

def configCli() -> Cli:
    global commands
    cli = Cli()
    # Arguments
    cmd, msg = "crear", ("<void or integer between(1-5)> --> " + 
            " creates and configures the number of servers especified\n " +
            "          (if void, 2 servers are created). It also initializes a load balancer" + 
            " and connects all vms with bridges")
    cli.addArg(cmd, description=msg, extraArg=True, choices=[1,2,3,4,5], default=2)
    commands[cmd] = repository.crear
    
    cmd, msg = "arrancar", "runs all the virtual machines already created (stopped or frozen)"
    cli.addArg(cmd, description=msg)
    commands[cmd] = repository.arrancar
    
    cmd, msg = "parar", "stops the virtual machines currently running"
    cli.addArg(cmd, description=msg)
    commands[cmd] = repository.parar
    
    cmd, msg = "destruir", "deletes every virtual machine created and all connections betweeen them"
    cli.addArg(cmd, description=msg)
    commands[cmd] = repository.destruir
    
    # Other functionalities
    cmd, msg = "pausar", "pauses the virtual machines currently running"
    cli.addArg(cmd, description=msg)
    commands[cmd] = repository.pausar
    
    cmd, msg = "lanzar", "executes the create and start commands in a row"
    cli.addArg(cmd, description=msg, extraArg=True, choices=[1,2,3,4,5], default=2)
    commands[cmd] = repository.lanzar

    cmd, msg = "añadir", "<integer between(1-4)> adds the number of servers specified (the program can't surpass 5 servers)"
    cli.addArg(cmd, description=msg, extraArg=True, choices=[1,2,3,4])
    commands[cmd] = repository.añadir
    
    cmd, msg = "eliminar", "<name of the server> deletes the server specified"
    cli.addArg(cmd, description=msg, extraArg=True)
    commands[cmd] = repository.eliminar
    
    cmd, msg = "show", "<diagram or state> shows information about the pupose of the program and it's current state"
    cli.addArg(cmd, description=msg, extraArg=True, choices=["diagram", "state"])
    commands[cmd] = repository.show
    
    cmd, msg = "xterm", "<void or vm_name> opens the terminal of a virtual machine or all of them if no name is given"
    cli.addArg(cmd, description=msg, extraArg=True, default="")
    commands[cmd] = repository.xterm
    
    #Flags/Options
    msg = "shows information about every process that is being executed"
    cli.addOption("-v", notCompatibleWith=["-d"], description=msg)
    msg = "option for debugging"
    cli.addOption("-d", notCompatibleWith=["-v"], description=msg)
    msg = "'quiet mode', doesn't show any msg during execution (only when an error occurs)"
    cli.addOption("-q", notCompatibleWith=["-v","-d"], description=msg)
    msg = "executes the action without asking confirmation"
    cli.addOption("-f", description=msg)
    msg = "opens the terminal window of the vms that are being started"
    cli.addOption("-t", description=msg)
    return cli


def configVerbosity(args:list):
    if "-d" in args:
        logLvl = logging.DEBUG
        args.remove("-d")
    elif "-v" in args:
        logLvl = logging.INFO
        args.remove("-v")
    elif "-q" in args:
        logLvl = logging.ERROR
        args.remove("-q")
    else:
        logLvl = logging.WARNING
    root_logger = logging.getLogger()
    root_logger.setLevel(logLvl) 