from . import data

data.init()

from . import classes
from . import devices
from . import utils

def start():
    data.registers.call("ready")
    print("Ready")