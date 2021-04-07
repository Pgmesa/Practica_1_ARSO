from bashCmds import createVms, startVms, stopVms, deleteVms
from CLInterface import Cli

# -------------------------------BASH HANDLER-------------------------------
# --------------------------------------------------------------------------
# Defines how the program works and how the command line is going to be read
# and interpreted. The bashCmd module is not coupled with this one, they are
# independent.

def execute(args:list):
    """Executes the command line order 'crear', 'arrancar', 'parar' or 'destruir'"""
    order = args[0]
    if order == "crear":
        createVms(args[1])
    elif order == "arrancar":
        startVms()
    elif order == "parar":
        stopVms()
    elif order == "destruir":
        deleteVms()
    
def configCli() -> Cli:
    cli = Cli()
    # Arguments
    msg = ("<void or integer between(1-5)> --> " + 
            " creates and configures the number of servers especified\n " +
            "          (if void, 2 servers are created). It also initializes a load balancer" + 
            " and connects all vms with bridges")
    cli.addArg("crear", description=msg, choices=[1,2,3,4,5], default=2)
    msg = "runs all the virtual machines already created"
    cli.addArg("arrancar", description=msg)
    msg = "stops the virtual machines currently running"
    cli.addArg("parar", description=msg)
    msg = "deletes every virtual machine created and all connections betweeen them"
    cli.addArg("destruir", description=msg)
    
    #Options
    msg = "shows information about every process that is being executed"
    cli.addOption("-v", ["-d"], description=msg)
    cli.addOption("-d", ["-v"])
    return cli
