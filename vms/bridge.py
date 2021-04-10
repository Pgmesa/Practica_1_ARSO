from vms.vm import VirtualMachine

class Bridge:
    
    used_by = []
    
    def __init__(self, name:str, ipv4:str, ipv4_net:bool, ipv6:str, ipv6_net:bool):
        self.name = name
        self.ipv4 = ipv4
        self.ipv4_net = ipv4_net
        self.ipv6 = ipv6
        self.ipv6_net = ipv6_net
        
    def attach(self, vm:VirtualMachine, ip:str):
        pass
    
    