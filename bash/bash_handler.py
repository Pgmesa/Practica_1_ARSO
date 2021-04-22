import logging

from dependencies.cli.cli import Cli
from dependencies.utils.decorators import timer
import bash.repository.commands as commands_rep

# ----------------------------BASH HANDLER----------------------------
# --------------------------------------------------------------------
# Define como se va a leer la linea de comandos y ejecuta las ordenes

commands = {}
# --------------------------------------------------------------------
@timer
def execute(args:list, flags:list):
    """Executes the commands of the program'"""
    order = args[0]
    command = commands[order]
    args.pop(0)
    command(*args, flg=flags)
        
# --------------------------------------------------------------------
def config_cli() -> Cli:
    global commands
    cli = Cli()
    # Arguments
    cmd = "crear"
    msg = (
        "<void or integer between(1-5)> --> " + 
        " creates and configures the number of servers especified\n " +
        "          (if void, 2 servers are created). It also " + 
        " initializes a load balancer and connects all vms with bridges"
    )
    cli.add_command(cmd, description=msg, extra_arg=True, 
                                choices=[1,2,3,4,5], default=2)
    opt = "--name"
    msg = ("<vm_names> allows to specify the " + 
                "name of the vms, 's_' is given if void")
    cli.commands[cmd].add_option(opt, description=msg, extra_arg=True, 
                                        multi=True, mandatory=True)
    commands[cmd] = commands_rep.crear
    
    cmd = "arrancar"
    msg = ("<void or vm_names> runs the virtual machines " + 
                " specified (stopped or frozen)")
    cli.add_command(cmd, description=msg, extra_arg=True, multi=True)
    commands[cmd] = commands_rep.arrancar
    
    cmd = "parar"
    msg = "stops the virtual machines currently running"
    cli.add_command(cmd, description=msg, extra_arg=True, multi=True)
    commands[cmd] = commands_rep.parar
    
    cmd = "destruir"
    msg = ("deletes every virtual machine created " +
                "and all connections betweeen them")
    cli.add_command(cmd, description=msg)
    commands[cmd] = commands_rep.destruir
    
    # Other functionalities
    cmd = "pausar"
    msg = "pauses the virtual machines currently running"
    cli.add_command(cmd, description=msg, extra_arg=True, multi=True)
    commands[cmd] = commands_rep.pausar

    cmd = "añadir"
    msg = ("<integer between(1-4)> adds the number of servers" +
                " specified (the program can't surpass 5 servers)")
    cli.add_command(cmd, description=msg, extra_arg=True, 
                                choices=[1,2,3,4], mandatory=True)
    opt = "--name"
    msg = ("<vm_names> allows to specify the name " +
                " of the vms, 's_' is given if void")
    cli.commands[cmd].add_option(opt, description=msg, extra_arg=True, 
                                        multi=True, mandatory=True)
    commands[cmd] = commands_rep.añadir
    
    cmd = "eliminar"
    msg = "<vm_names> deletes the vms specified"
    cli.add_command(cmd, description=msg, extra_arg=True,  multi=True)
    commands[cmd] = commands_rep.eliminar
    
    cmd = "show"
    msg = ("<diagram or state> shows information about " + 
                "the pupose of the program and it's current state")
    cli.add_command(cmd, description=msg, extra_arg=True, 
                            choices=["diagram", "state"], mandatory=True)
    commands[cmd] = commands_rep.show
    
    cmd = "xterm"
    msg = ("<void or vm_name> opens the terminal the vms " + 
                "specified or all of them if no name is given")
    cli.add_command(cmd, description=msg, extra_arg=True, multi=True)
    commands[cmd] = commands_rep.xterm
    
    #Flags/Options
    msg = "shows information about every process that is being executed"
    cli.add_flag("-v", notCompatibleWithFlags=["-d"], description=msg)
    msg = "option for debugging"
    cli.add_flag("-d", notCompatibleWithFlags=["-v"], description=msg)
    msg = ("'quiet mode', doesn't show any msg " + 
            "during execution (only when an error occurs)")
    cli.add_flag("-q", notCompatibleWithFlags=["-v","-d"], description=msg)
    msg = "executes the action without asking confirmation"
    cli.add_flag("-f", description=msg)
    msg = "opens the terminal window of the vms that are being started"
    cli.add_flag("-t", description=msg)
    msg = "launches the container"
    cli.add_flag("-l", description=msg)
    return cli

# --------------------------------------------------------------------
def config_verbosity(flags:list):
    if "-d" in flags:
        logLvl = logging.DEBUG
    elif "-v" in flags:
        logLvl = logging.INFO
    elif "-q" in flags:
        logLvl = logging.ERROR
    else:
        logLvl = logging.WARNING
    root_logger = logging.getLogger()
    root_logger.setLevel(logLvl) 

# --------------------------------------------------------------------