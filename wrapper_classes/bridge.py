import subprocess

class LxcNetworkError(Exception):
    pass

class Bridge:
    
    def __init__(self,
                 name:str,
                 ethernet:str,
                 ipv4_nat:bool=False, ipv4_addr:str=None,
                 ipv6_nat:bool=False, ipv6_addr:str=None):
        self.name = name
        if self.name == "lxdbr0":
            self.is_default = True
        else:
            self.is_default = False
        if ipv4_nat == True:
            self.ipv4_nat = "true"
        else:
            self.ipv4_nat = "false"
        if ipv4_addr != None:
            self.ipv4_addr = ipv4_addr
        else:
            self.ipv4_addr = "none"
        if ipv6_nat == True:
            self.ipv6_nat = "true"
        else:
            self.ipv6_nat = "false"
        if ipv6_addr != None:
            self.ipv6_addr = ipv6_addr
        else:
            self.ipv6_addr = "none"   
        # El ethernet depende de que bridge se ha creado primero
        # no depende del nombre ni la ip. Por tanto siempre (lxdbr0 -> eth0)
        self.ethernet = ethernet
        self.used_by = []
    
    def run(self, cmd:list):
        process = subprocess.run(
            cmd, 
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE # No queremos que salga en consola
        )
        outcome = process.returncode
        if outcome != 0:
            err_msg = (f" Fallo al ejecutar el comando {cmd}.\n" +
                            "Mensaje de error de subprocess: ->")
            err_msg += process.stderr.decode().strip()[6:]
            raise LxcNetworkError(err_msg)
    
    def add_vm(self, vm_name:str):
        cmd = ["lxc", "network", "attach" ,self.name, vm_name, self.ethernet]
        self.run(cmd)
        self.used_by.append(vm_name)
    
    def create(self):
        if not self.is_default:
            cmd = ["lxc","network","create", self.name, "-q"]
            self.run(cmd)   
        self.run(["lxc","network", "set", self.name, "ipv4.nat", self.ipv4_nat])
        self.run(["lxc", "network", "set", self.name, "ipv4.address", self.ipv4_addr])
        self.run(["lxc", "network", "set", self.name, "ipv6.nat", self.ipv6_nat])
        self.run(["lxc", "network", "set", self.name, "ipv6.address", self.ipv6_addr])
    
    def delete(self):
        if not self.is_default:
            cmd = ["lxc","network","delete", self.name, "-q"]
            self.run(cmd)
        else:
            self.run(["lxc","network", "set", self.name, "ipv4.nat", "false"])
            self.run(["lxc", "network", "set", self.name, "ipv4.address", "none"])
        
    def __str__(self):
        return self.name
    