
class Cli:
    def __init__(self):
        self.arguments = []
        self.options = [Option("-h", description="shows information" + 
                                            " about the commands available")]
        
    def addArg(self, name:str, choices:list=None, default:any=None, description:str=None):
        self.arguments.append(Argument(name, choices, default, description))
    
    def addOption(self, option:str, notCompatibleWith:list=[], description=None):
        self.options.append(Option(option, notCompatibleWith, description))
    
    def processCmdline (self,inArgs:list) -> list:
        inOpts = []
        # Miramos a ver si alguna de las opciones validas 
        # esta en la linea de comandos introducida
        for opt in self.options:
            if opt.name in inArgs:
                if opt.name == "-h":
                    self.printHelp()
                    # No hay nada mas que hacer
                    return None
                inOpts.append(opt)
        # Miramos si de las opciones introducidas, 
        # hay alguna no compatible con otra
        for opt1 in inOpts:
            for opt2 in inOpts:
                if not opt1.ncw == None and opt2.name in opt1.ncw:
                    errmsg = f"Las opciones '{opt1.name}' y '{opt2.name}' no son compatibles"
                    raise cmdLineError(errmsg)
        # Miramos a ver si despues de eliminar la opcion ya procesada
        # esta vuelve a aparecer => Se ha introducido 2 veces.
        for opt in inOpts:
            inArgs.remove(opt.name)
            if opt.name in inArgs:
                raise cmdLineError (f"Opcion '{opt.name}' repetida")
            # Guardamos los nombres en vez del objeto Option
            inOpts[inOpts.index(opt)] = opt.name
        
        inArgs.pop(0)
        for arg in self.arguments:
            if len(inArgs) == 0:
                raise cmdLineError("No se han proporcionado argumentos")
            if inArgs[0] in arg.name:
                if len(inArgs) > 1:
                    if not arg.choices == None:
                        try:
                            seconsArg = int(inArgs[1])
                        except:
                            seconsArg = inArgs[1]
                        if seconsArg in arg.choices:
                            return [arg.name, arg.choices[arg.choices.index(seconsArg)]] + inOpts
                elif not arg.default == None:
                    return [arg.name, arg.default] + inOpts
                else:
                    return [arg.name] + inOpts
        raise cmdLineError("Argumentos incorrectos")
    
    def printHelp(self):
        print(" python3 __main__ [commands] <options>")
        print(" + Commands: ")
        for arg in self.arguments:
            print(f"    -> {arg.name} --> {arg.description}")
        print(" + Options: ")   
        for opt in self.options:
            if not opt.description == None:
                print(f"    -> {opt.name} --> {opt.description}")
            else:
                print(f"    -> {opt.name}")

class cmdLineError(Exception):
    def __init__(self, msg:str):
        hlpm = "\nIntroduce el parametro -h para acceder a la ayuda"
        super().__init__(msg + hlpm)

class Argument:
    def __init__(self, name:str, choices:list=None, 
                    default:any=None, description:str=None):
        self.name = name
        self.choices = choices
        self.default = default
        self.description = description 
    
    def __str__(self):
        return self.name 
    
class Option:
    def __init__(self, option:str, 
                    notCompatibleWith:list=[], description:str=None):
        self.name = option
        self.ncw = notCompatibleWith
        self.description = description
        
    def __str__(self):
        return self.name 
        
