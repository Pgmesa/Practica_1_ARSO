import subprocess
 
# Possible states of the virtual machines
NOT_INIT = "NOT INITIALIZED"
STOPPED = "STOPPED"
FROZEN = "FROZEN"
RUNNING = "RUNNING"
DELETED = "DELETED"


class LxcError(Exception):
    pass

class Container:
    
    def __init__(self, name:str, container_image:str, tag:str=""):
        self.name = name
        self.container_image = container_image
        self.state = NOT_INIT
        self.tag = tag
        self.networks = {}
        
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
            raise LxcError(err_msg)    
        
    def add_to_network(self, eth:str, with_ip:str):
        cmd = ["lxc","config","device","set", self.name, eth,"ipv4.address", with_ip]
        self.run(cmd)
        self.networks[eth] = with_ip

    def open_terminal(self):
        if self.state != RUNNING:
            raise LxcError(f" {self.tag} '{self.name}' esta '{self.state}' " +
                                "y no puede abrir la terminal")
        subprocess.Popen([
            "xterm","-fa", "monaco", "-fs", "13", "-bg", "black",
            "-fg", "green", "-e", f"lxc exec {self.name} bash"
        ])
    
    def init(self) -> LxcError:
        if self.state != NOT_INIT:
            raise LxcError(f" {self.tag} '{self.name}' esta '{self.state}' " +
                                "y no puede ser inicializado de nuevo")
        self.run(["lxc", "init", self.container_image, self.name])  
        self.state = STOPPED
        # Limiting the resources of the vms created
        self.run(["lxc", "config", "set", self.name, "limits.cpu.allowance", "40ms/200ms"])
        self.run(["lxc", "config", "set", self.name, "limits.memory", "1024MB"]) 
        self.run(["lxc", "config", "set", self.name, "limits.cpu", "2"])
        
    def start(self):
        if self.state != STOPPED and self.state != FROZEN:
            raise LxcError(f" {self.tag} '{self.name}' esta '{self.state}' " +
                                "y no puede ser arrancado")
        self.run(["lxc", "start", self.name])  
        self.state = RUNNING
        
    def stop(self):
        if self.state != RUNNING and self.state != FROZEN:
            raise LxcError(f" {self.tag} '{self.name}' esta '{self.state}' " +
                                "y no puede ser detenido")
        self.run(["lxc", "stop", self.name])  
        self.state = STOPPED
        
    def delete(self):
        if self.state != STOPPED:
            raise LxcError(f" {self.tag} '{self.name}' esta '{self.state}' " +
                                "y no puede ser eliminado")
        self.run(["lxc", "delete", self.name])  
        self.state = DELETED
    
    def pause(self):
        if self.state != RUNNING:
            raise LxcError(f" {self.tag} '{self.name}' esta '{self.state}' " +
                                "y no puede ser pausado")
        self.run(["lxc", "pause", self.name])  
        self.state = FROZEN
    
    def launch(self):
        self.init()
        self.start()
    
    def __str__(self):
        return self.name