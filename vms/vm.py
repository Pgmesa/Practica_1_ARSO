import subprocess
 
# Possible states of the virtual machines
NOT_INIT = "NOT INITIALIZED"
STOPPED = "STOPPED"
FROZEN = "FROZEN"
RUNNING = "RUNNING"
DELETED = "DELETED"


class LxcError(Exception):
    pass

class VirtualMachine:
    
    def __init__(self, name:str, container_image:str, tag:str=""):
        self.name = name
        self.container_image = container_image
        self.state = NOT_INIT
        self.tag = tag
        self.networks = {}
        
    def add_to_network(self, eth:str, with_ip:str):
        process = subprocess.Popen([
            "lxc","config","device","set", self.name,
            eth,"ipv4.address", with_ip
        ])
        outcome = process.wait()
        if outcome != 0:
            errmsg = process.stderr.read().decode().strip()[6:]
            raise LxcError(errmsg)
        self.networks[eth] = with_ip
    
    def execute_order(self, order:str, final_state:str):
        cmd = ["lxc", order, self.container_image, self.name]
        if order != "init":
            cmd.pop(2)
        process = subprocess.Popen(
            cmd, 
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE # No queremos que salga en consola
        )
        outcome = process.wait()
        if outcome == 0:
            self.state = final_state
            if order == "start":
                subprocess.Popen([
                "xterm","-fa", "monaco", "-fs", "13", "-bg", "black",
                "-fg", "green", "-e", f"lxc exec {self.name} bash"
                ])
        else:
            err_msg = process.stderr.read().decode().strip()[6:]
            raise LxcError(err_msg) 
    
    def init(self):
        if self.state != NOT_INIT:
            raise LxcError(f" {self.tag} '{self.name}' esta '{self.state}' " +
                                "y no puede ser inicializado de nuevo")
        self.execute_order("init", final_state=STOPPED)  
        # Limiting the resources of the vms created
        subprocess.call(["lxc", "config", "set", self.name, "limits.cpu.allowance", "40ms/200ms"])
        subprocess.call(["lxc", "config", "set", self.name, "limits.memory", "256MB"]) 
        subprocess.call(["lxc", "config", "set", self.name, "limits.cpu", "2"])
        
    def start(self):
        if self.state != STOPPED:
            raise LxcError(f" {self.tag} '{self.name}' esta '{self.state}' " +
                                "y no puede ser arrancado")
        self.execute_order("start", final_state=RUNNING) 
        
    def stop(self):
        if self.state != RUNNING:
            raise LxcError(f" {self.tag} '{self.name}' esta '{self.state}' " +
                                "y no puede ser detenido")
        self.execute_order("stop", final_state=STOPPED) 
        
    def delete(self):
        if self.state != STOPPED:
            raise LxcError(f" {self.tag} '{self.name}' esta '{self.state}' " +
                                "y no puede ser eliminado")
        self.execute_order("delete", final_state=DELETED) 
    
    def pause(self):
        self.execute_order("pause", final_state=FROZEN) 
    
    def launch(self):
        self.init()
        self.start()
    
    def __str__(self):
        return self.name