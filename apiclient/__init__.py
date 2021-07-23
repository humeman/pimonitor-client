version = "1.0.0a"

import time
timer = time.time()

from . import classes
from . import loops
from . import utils


from . import data

data.init()

def start():
    data.start()