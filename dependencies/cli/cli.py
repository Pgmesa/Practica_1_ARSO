
from .aux_classes import Command, Flag,  CmdLineError


# ------- Command Line Interface
class Cli:
    def __init__(self):
        self.commands = {}
        self.flags = {"-h": Flag("-h", description="shows information" + 
                                                    " about the commands available")}
        
    def add_command(self, command:Command):
        self.commands[command.name] = command 
    
    def add_flag(self, flag:Flag):
        self.flags[flag.name] = flag
        
    def process_cmdline(self, args:list) -> list:
        args.pop(0) # Eliminamos el nombre del programa
        if "-h" in args: 
            self.printHelp()
            return None

        inFlags = []
        # Miramos a ver si alguno de los flags validos esta en la linea de comandos introducida
        for arg in args:
            for validFlag in self.flags.values():
                if arg == validFlag.name:
                    if len(inFlags) > 0:
                        # Comprobamos que son flags compatibles
                        for flag in inFlags:
                            if flag.name in validFlag.ncwf or validFlag.name in flag.ncwf:
                                errmsg = f"Las opciones '{flag}' y '{validFlag}' no son compatibles"
                                raise CmdLineError(errmsg)
                    inFlags.append(validFlag)
        # Eliminamos los flags ya procesadas de la linea de comandos  
        for flag in inFlags: args.remove(flag.name)
        # Guardamos los nombres de los flags en vez del objeto Flag entero (ya no nos hace falta)
        inFlags = list(map(lambda flag: str(flag), inFlags))
        # Revisamos si alguno de los comandos validos esta en la linea de comandos introducida
        for cmd in self.commands.values():
            if len(args) == 0:
                raise CmdLineError("No se han proporcionado argumentos")
            if args[0] == cmd.name:
                # Separamos por partes la linea de comandos
                ant = args[0]; parts = {ant: ""}; last_index = 1
                for i, arg in enumerate(args):
                    if arg in cmd.options:
                        parts[ant] = args[last_index:i]
                        last_index = i + 1
                        ant = arg
                parts[ant] = args[last_index:]
                # Vemos si cada parte es válida y la guardamos en un diccionario
                processed_line = {"cmd": {}, "options": {}, "flags": []}
                for cmd_name, part in parts.items():
                    try:
                        command = cmd.options[cmd_name]
                        key = "options"
                    except KeyError:
                        command = cmd
                        key = "cmd"
                    dict_page = {command.name: self.check_command(command, part)}
                    processed_line[key] = dict_page
                processed_line["flags"] = inFlags
                return processed_line
        raise CmdLineError(f"El comando '{args[0]}' no se reconoce")
    
    @staticmethod
    def check_command(cmd, args):
        if len(args) > 0:
            if len(args) > 1 and not cmd.multi: 
                err_msg = ("No se permite mas de 1 opcion extra" +
                                f" en el comando '{cmd.name}'. Comandos incorrectos -> {args[1:]}")
                raise CmdLineError(err_msg)
            if cmd.extra_arg:
                extra_args = []
                for extra in args:
                    try:
                        extra_args.append(int(extra))
                    except:
                        extra_args.append(extra)
                if cmd.choices == None:
                    return extra_args
                #Todos los extra args deben estar en choices
                for extra in extra_args:
                    if extra not in cmd.choices:
                        break
                #Si completa el bucle es que todos son validos
                else:
                    return extra_args
                raise CmdLineError(f"El parametro extra '{args[0]}' no es valido")
            else:
                raise CmdLineError(f"El comando '{cmd.name}' no admite parametros extra")
        elif not cmd.default == None:
            return [cmd.default]
        elif not cmd.mandatory:
            return []
        else:
            raise CmdLineError(f"El comando '{cmd.name}' requiere un parametro extra")
    
    def printHelp(self):
        print(" python3 __main__ [commands] <options> <flags>")
        print(" + Commands: ")
        for arg in self.commands.values():
            print(f"    -> {arg.name} --> {arg.description}")
            if len(arg.options) > 0:
                print(f"        - options:")
                for opt in arg.options.values():
                    info = f"=> '{opt.name}' --> {opt.description}"
                    print("          ", info)
        print(" + Flags: ")   
        for flag in self.flags.values():
            if not flag.description == None:
                print(f"    -> {flag.name} --> {flag.description}")
            else:
                print(f"    -> {flag.name}")


        
