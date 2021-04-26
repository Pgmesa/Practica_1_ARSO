
import logging

import bash.repository.commands as commands_rep
from dependencies.cli.cli import Cli
from dependencies.cli.aux_classes import Command, Flag, CmdLineError
from dependencies.utils.decorators import timer


# ----------------------------BASH HANDLER----------------------------
# --------------------------------------------------------------------
# Define como se va a leer la linea de comandos y ejecuta las ordenes

commands = {}
# --------------------------------------------------------------------
@timer
def execute(args:list):
    """Executes the commands of the program'"""
    for cmd_name, cmd in commands.items():
        if cmd_name in args["cmd"]:
            principal = args.pop("cmd").pop(cmd_name)
            secundary = args
            cmd(*principal, **secundary)
            break
        
# --------------------------------------------------------------------
def config_cli() -> Cli:
    global commands
    cli = Cli()
    # Arguments
    cmd_name = "crear"
    msg = (
        "<void or integer between(1-5)> --> " + 
        "deploys a server platform\n           with the number " +
        "of servers especified (if void, 2 servers are created). It\n " + 
        "          also initializes a load balancer that acts as a bridge " +
        "between the servers\n           and the clients. Everything is " +
        "connected by 2 virtual bridges"
    )
    crear = Command(cmd_name, description=msg, extra_arg=True, 
                                choices=[1,2,3,4,5], default=2)
    msg = ("<server_names> allows to specify the name of the servers, " + 
           "\n                      by default 's_' is given to each server")
    crear.add_option("--name", description=msg, extra_arg=True, 
                                        multi=True, mandatory=True)
    msg = ("<alias or fingerprint> allows to specify the image of the " +
           "containers,\n                      by default ubuntu:18.04 is used")
    crear.add_option("--image", description=msg, extra_arg=True, mandatory=True)
    msg ="<alias or fingerprint> allows to specify the image of the servers"
    crear.add_option("--simage", description=msg, extra_arg=True, mandatory=True)
    msg = "<alias or fingerprint> allows to specify the image of the load balancer"
    crear.add_option("--climage", description=msg, extra_arg=True, mandatory=True)
    msg = "<alias or fingerprint> allows to specify the image of the client"
    crear.add_option("--lbimage", description=msg, extra_arg=True, mandatory=True)
    cli.add_command(crear)
    commands[cmd_name] = commands_rep.crear
    
    cmd_name = "arrancar"
    msg = ("<void or container_names> runs the containers specified, " +
           "if void\n           all containers are runned")
    arrancar = Command(cmd_name, description=msg, extra_arg=True, multi=True)
    cli.add_command(arrancar)
    commands[cmd_name] = commands_rep.arrancar
    
    cmd_name = "parar"
    msg = ("<void or container_names> stops the containers currently " +
          "running,\n           if void all containers are stopped")
    parar = Command(cmd_name, description=msg, extra_arg=True, multi=True)
    cli.add_command(parar)
    commands[cmd_name] = commands_rep.parar
    
    cmd_name = "destruir"
    msg = ("deletes every component of the platform created")
    destruir = Command(cmd_name, description=msg)
    cli.add_command(destruir)
    commands[cmd_name] = commands_rep.destruir
    
    # Other functionalities
    cmd_name = "pausar"
    msg = ("<void or container_names> pauses the containers currently " +
          "running,\n           if void all containers are stopped")
    pausar = Command(cmd_name, description=msg, extra_arg=True, multi=True)
    cli.add_command(pausar)
    commands[cmd_name] = commands_rep.pausar

    cmd_name = "añadir"
    msg = ("<integer between(1-5)> adds the number of servers specified " +
           " (the\n           program can't surpass 5 servers)")
    añadir = Command(cmd_name, description=msg, extra_arg=True, 
                                choices=[1,2,3,4,5], mandatory=True)
    msg = ("<server_names> allows to specify the name of the servers, " + 
           "\n                      by default 's_' is given to each server")
    añadir.add_option("--name", description=msg, extra_arg=True, 
                                        multi=True, mandatory=True)
    msg ="<alias or fingerprint> allows to specify the image of the servers"
    añadir.add_option("--simage", description=msg, extra_arg=True, mandatory=True)
    cli.add_command(añadir)
    commands[cmd_name] = commands_rep.añadir
    
    cmd_name = "eliminar"
    msg = ("<void or server_names> deletes the servers specified, if void " +
          "\n           all servers are deleted")
    eliminar = Command(cmd_name, description=msg, extra_arg=True,  multi=True)
    cli.add_command(eliminar)
    commands[cmd_name] = commands_rep.eliminar
    
    cmd_name = "show"
    msg = ("<diagram, state or files> shows information about the program. " + 
          "'state' shows\n           information about every machine/component " +
          "of the platform, 'diagram' displays \n           a diagram that " +
          "explains the structure of the platform and 'files' shows the " + 
          "files \n           structure of the code and the external " +
          "dependencies of the program")
    show = Command(cmd_name, description=msg, extra_arg=True, 
                            mandatory=True, choices=["diagram", "state", "files"])
    cli.add_command(show)
    commands[cmd_name] = commands_rep.show
    
    cmd_name = "term"
    msg = ("<void or container_names> opens the terminal of the containers " + 
           "\n           specified or all of them if no name is given")
    term = Command(cmd_name, description=msg, extra_arg=True, multi=True)
    cli.add_command(term)
    commands[cmd_name] = commands_rep.term
    
    #Flags/Options
    msg = "shows information about every process that is being executed"
    verbosity = Flag("-v", notCompatibleWithFlags=["-d"], description=msg)
    cli.add_flag(verbosity)
    msg = "option for debugging"
    debugging = Flag("-d", notCompatibleWithFlags=["-v"], description=msg)
    cli.add_flag(debugging)
    msg = ("'quiet mode', doesn't show any msg " + 
            "during execution (only when an error occurs)")
    quiet = Flag("-q", notCompatibleWithFlags=["-v","-d"], description=msg)
    cli.add_flag(quiet)
    msg = "executes the action without asking confirmation"
    force = Flag("-f", description=msg)
    cli.add_flag(force)
    msg = "opens the terminal window of the containers that are being runned"
    terminal = Flag("-t", description=msg)
    cli.add_flag(terminal)
    msg = "launches the container"
    launch = Flag("-l", description=msg)
    cli.add_flag(launch)
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