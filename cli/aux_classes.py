
class CmdLineError(Exception):
    def __init__(self, msg:str, _help=True):
        hlpm = "\nIntroduce el parametro -h para acceder a la ayuda"
        if _help: 
            msg += hlpm
        super().__init__(msg)

class Command:
    def __init__(self, name:str, extra_arg:any=False, mandatory=False, multi=False,
                    choices:list=None, default:any=None, description:str=None):
        self.name = name
        self.extra_arg = extra_arg
        self.choices = choices
        self.default = default
        self.description = description 
        self.mandatory = mandatory
        self.multi = multi
        self.options = {}
    
    def add_option(self, name:str, extra_arg:any=False, mandatory=False, multi=False,
                    choices:list=None, default:any=None, description:str=None):
        self.options[name] = Command(
            name,
            extra_arg=extra_arg, 
            mandatory=mandatory, 
            multi=multi,
            choices=choices, 
            default=default, 
            description=description
        )
    
    def __str__(self) -> str:
        return self.name 
    
class Flag:
    def __init__(self, flag:str, notCompatibleWithFlags:list=[], 
                 description:str=None):
        self.name = flag
        self.ncwf = notCompatibleWithFlags + [self.name]
        self.description = description
        
    def __str__(self) -> str:
        return self.name 