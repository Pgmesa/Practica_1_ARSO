
# --------------------------------TOOLS--------------------------------
# ---------------------------------------------------------------------
# Gathers a group of useful functions that may be used in other important
# functions or in debugging.

config_file = str("network:\n" +
                  "    version: 2\n" + 
                  "    ethernets:\n" + 
                  "        eth0:\n" + 
                  "            dhcp4: true\n" + 
                  "        eth1:\n" + 
                  "            dhcp4: true")

def create_yaml():
    """Creates a file with the 'configuration_file' info"""
    with open("50-cloud-init.yaml", "w") as file:
        file.write(config_file)

def isPositiveInt (var) -> bool:
    """Checks if a variable is a positive integer"""
    try:
        integer = int(var)
        if integer > 0:
            return True
        else:
            return False
    except:
        return False
    
def numInBetween(num: int or float, Range:list or tuple) -> bool:
    """Checks if a number is in between other 2. 
        A tuple would mean a closed range and a list an open range"""
    if type(Range) == list:
        if num >= Range[0] and num <= Range[1]:
            return True
    elif type(Range) == tuple:
        if num > Range[0] and num < Range[1]:
            return True
    return False
