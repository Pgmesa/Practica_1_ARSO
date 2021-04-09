from vms.controllers import createVms, startVms, stopVms, deleteVms
from cli.cli import Cli

# -------------------------------BASH HANDLER-------------------------------
# --------------------------------------------------------------------------
# Defines how the program works and how the command line is going to be read
# and interpreted. The bashCmd module is not coupled with this one, they are
# independent.

def execute(args:list):
    """Executes the commands of the program'"""
    order = args[0]
    if order == "crear":
        createVms(args[1])
    elif order == "arrancar":
        startVms()
    elif order == "parar":
        stopVms()
    elif order == "destruir":
        deleteVms()
    elif order == "añadir":
        print(args)
    elif order == "eliminar":
        print(args)
    
def configCli() -> Cli:
    cli = Cli()
    # Arguments
    msg = ("<void or integer between(1-5)> --> " + 
            " creates and configures the number of servers especified\n " +
            "          (if void, 2 servers are created). It also initializes a load balancer" + 
            " and connects all vms with bridges")
    cli.addArg("crear", description=msg, extraArg=True, choices=[1,2,3,4,5], default=2)
    msg = "runs all the virtual machines already created"
    cli.addArg("arrancar", description=msg)
    msg = "stops the virtual machines currently running"
    cli.addArg("parar", description=msg)
    msg = "deletes every virtual machine created and all connections betweeen them"
    cli.addArg("destruir", description=msg)
    # Other functionalities
    msg = "<integer between(1-5)> adds the number of servers specified (it can't surpass 5 servers)"
    cli.addArg("añadir", description=msg, extraArg=True, choices=[1,2,3,4])
    msg = "<name of the server> deletes the server specified"
    cli.addArg("eliminar", description=msg, extraArg=True)
    
    #Options
    msg = "shows information about every process that is being executed"
    cli.addOption("-v", notCompatibleWith=["-d"], description=msg)
    msg = "option for debugging"
    cli.addOption("-d", notCompatibleWith=["-v"], description=msg)
    return cli
