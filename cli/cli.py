from functools import reduce

from cli.aux_classes import Command, Flag,  CmdLineError

# ------- Command Line Interface
class Cli:
    def __init__(self):
        self.commands = {}
        self.flags = {"-h": Flag("-h", description="shows information" + 
                                                    " about the commands available")}
        
    def add_command(self, name:str, extra_arg:bool=False, mandatory=False, multi=False,
                            choices:list=None, default:any=None, description:str=None):
        self.commands[name] = Command(
            name,
            extra_arg=extra_arg, 
            mandatory=mandatory, 
            multi=multi,
            choices=choices, 
            default=default, 
            description=description
        )
    
    def add_flag(self, flag:str, notCompatibleWithFlags:list=[], description:str=None):
        self.flags[flag] = Flag(
            flag, 
            notCompatibleWithFlags=notCompatibleWithFlags,
            description=description
        )
        
    def process_cmdline(self, args:list) -> list:
        args.pop(0) # Eliminamos el nombre del programa
        if "-h" in args: 
            self.printHelp()
            return None, "-h"

        inFlags = []
        # Miramos a ver si alguna de las opciones validas esta en la linea de comandos introducida
        for arg in args:
            for validFlag in self.flags.values():
                if arg == validFlag.name:
                    if len(inFlags) > 0:
                        # Comprobamos que son opciones compatibles
                        for flag in inFlags:
                            if flag.name in validFlag.ncwf or validFlag.name in flag.ncwf:
                                errmsg = f"Las opciones '{flag}' y '{validFlag}' no son compatibles"
                                raise CmdLineError(errmsg)
                    inFlags.append(validFlag)
        # Eliminamos las opciones ya procesadas de la linea de comandos  
        for flag in inFlags: args.remove(flag.name)
        # Guardamos los nombres de las opciones en vez del objeto Option entero (ya no nos hace falta)
        inFlags = list(map(lambda flag: str(flag), inFlags))

        for cmd in self.commands.values():
            if len(args) == 0:
                raise CmdLineError("No se han proporcionado argumentos")
            if args[0] == cmd.name:
                ant = args[0]; parts = {ant: ""}; last_index = 0
                for i, arg in enumerate(args):
                    if arg in cmd.options:
                        parts[ant] = args[:i]
                        last_index = i
                        ant = arg
                parts[ant] = args[last_index:]
                
                processed_line = []
                for opt_name, part in parts.items():
                    try:
                        opt = cmd.options[opt_name]
                    except KeyError:
                        opt = cmd
                    processed_line += self.check_command(part, opt)
                return processed_line, inFlags
        raise CmdLineError(f"El comando '{args[0]}' no se reconoce")
    
    @staticmethod
    def check_command(args, cmd):
        if len(args) > 1:
            if len(args) > 2 and not cmd.multi: 
                err_msg = ("No se permite mas de 1 opcion extra" +
                                f" en el comando '{cmd.name}'. Comandos incorrectos -> {args[2:]}")
                raise CmdLineError(err_msg)
            if cmd.extra_arg:
                extra_args = []
                for extra in args[1:]:
                    try:
                        extra_args.append(int(extra))
                    except:
                        extra_args.append(extra)
                if cmd.choices == None:
                    return [cmd.name] + extra_args
                #Todos los extra args deben estar en choices
                for extra in extra_args:
                    if extra not in cmd.choices:
                        break
                #Si completa el bucle es que todos son validos
                else:
                    return [cmd.name] + extra_args
                raise CmdLineError(f"El parametro extra '{args[1]}' no es valido")
            else:
                raise CmdLineError(f"El comando '{args[0]}' no admite parametros extra")
        elif not cmd.default == None:
            return [cmd.name, cmd.default]
        elif not cmd.mandatory:
            return [cmd.name]
        else:
            raise CmdLineError(f"El comando '{args[0]}' requiere un parametro extra")
    
    def printHelp(self):
        print(" python3 __main__ [commands] <options/flags>")
        print(" + Commands: ")
        for arg in self.commands.values():
            print(f"    -> {arg.name} --> {arg.description}")
            for alt in arg.options.values():
                print(f"        => option '{alt.name}' --> {alt.description}")
        print(" + Flags: ")   
        for flag in self.flags.values():
            if not flag.description == None:
                print(f"    -> {flag.name} --> {flag.description}")
            else:
                print(f"    -> {flag.name}")


        
