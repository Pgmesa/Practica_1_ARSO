from functools import reduce

from cli.aux_classes import Option, Argument, CmdLineError

# ------- Command Line Interface
class Cli:
    def __init__(self):
        self.arguments = []
        self.options = [Option("-h", description="shows information" + 
                                            " about the commands available")]
        self.strArgs = []
        self.strOpts = ["-h"]
        
    def addArg(self, name:str, extraArg:bool=False,
                    choices:list=None, default:any=None, description:str=None):
        self.arguments.append(Argument(name,extraArg=extraArg,
                                        choices=choices, default=default, description=description))
        self.strArgs.append(name)
    
    def addOption(self, option:str, notCompatibleWith:list=[], description:str=None):
        self.options.append(Option(option, notCompatibleWith=notCompatibleWith,
                                        description=description))
        self.strOpts.append(option)
    def processCmdline (self,inArgs:list) -> list:
        inArgs.pop(0) # Eliminamos el nombre del programa
        if "-h" in inArgs: 
            self.printHelp()
            return None

        inOpts = []
        # Miramos a ver si alguna de las opciones validas esta en la linea de comandos introducida
        for arg in inArgs:
            for validOpt in self.options:
                if arg == validOpt.name:
                    if len(inOpts) > 0:
                        # Comprobamos que son opciones compatibles
                        for opt in inOpts:
                            if opt.name in validOpt.ncw or validOpt.name in opt.ncw:
                                errmsg = f"Las opciones '{opt}' y '{validOpt}' no son compatibles"
                                raise CmdLineError(errmsg)
                    inOpts.append(validOpt)
        # Eliminamos las opciones ya procesadas de la linea de comandos  
        for opt in inOpts: inArgs.remove(opt.name)
        # Guardamos los nombres de las opciones en vez del objeto Option entero (ya no nos hace falta)
        inOpts = list(map(lambda opt: str(opt), inOpts))

        for arg in self.arguments:
            if len(inArgs) == 0:
                raise CmdLineError("No se han proporcionado argumentos")
            if inArgs[0] == arg.name:
                if len(inArgs) > 1:
                    if len(inArgs) > 2: 
                        # Lo concatenamos para que quede mas bonito
                        wrongArgs = reduce(lambda string, arg: f"{string} {arg}", inArgs[1:])
                        raise CmdLineError(f"No se reconocen los comandos: {wrongArgs}")
                    if arg.extraArg:
                        try:
                            secondArg = int(inArgs[1])
                        except:
                            secondArg = inArgs[1]
                        if arg.choices == None:
                            return [arg.name, secondArg] + inOpts
                        elif secondArg in arg.choices:
                            return [arg.name, arg.choices[arg.choices.index(secondArg)]] + inOpts
                        raise CmdLineError(f"El parametro extra '{inArgs[1]}' no es valido")
                    else:
                        raise CmdLineError(f"El comando '{inArgs[0]}' no admite parametros extra")
                elif not arg.default == None:
                    return [arg.name, arg.default] + inOpts
                elif not arg.extraArg:
                    return [arg.name] + inOpts
                else:
                    raise CmdLineError(f"El comando '{inArgs[0]}' requiere un parametro extra")
        raise CmdLineError(f"El comando '{inArgs[0]}' no se reconoce")
    
    def printHelp(self):
        print(" python3 __main__ [commands] <options/flags>")
        print(" + Commands: ")
        for arg in self.arguments:
            print(f"    -> {arg.name} --> {arg.description}")
        print(" + Options/Flags: ")   
        for opt in self.options:
            if not opt.description == None:
                print(f"    -> {opt.name} --> {opt.description}")
            else:
                print(f"    -> {opt.name}")


        
