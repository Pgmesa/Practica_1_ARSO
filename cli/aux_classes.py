
class CmdLineError(Exception):
    def __init__(self, msg:str, _help=True):
        hlpm = "\nIntroduce el parametro -h para acceder a la ayuda"
        if _help: 
            msg += hlpm
        super().__init__(msg)

class Argument:
    def __init__(self, name:str, extraArg:any=False, mandatory=False, multi=False,
                    choices:list=None, default:any=None, description:str=None):
        self.name = name
        self.extraArg = extraArg
        self.choices = choices
        self.default = default
        self.description = description 
        self.mandatory = mandatory
        self.multi = multi
        self.alternatives = {}
    
    def add_alternative(self, name:str, extraArg:any=False, mandatory=False, multi=False,
                    choices:list=None, default:any=None, description:str=None):
        self.alternatives[name] = Argument(
            name,
            extraArg=extraArg, 
            mandatory=mandatory, 
            multi=multi,
            choices=choices, 
            default=default, 
            description=description
        )
    
    def __str__(self) -> str:
        return self.name 
    
class Option:
    def __init__(self, option:str, 
                    notCompatibleWith:list=[], description:str=None):
        self.name = option
        self.ncw = notCompatibleWith + [self.name]
        self.description = description
        
    def __str__(self) -> str:
        return self.name 