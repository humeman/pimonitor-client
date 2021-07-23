import gpio
from gpio.utils.registers import RegisterHandler

def init():
    global registers
    registers = RegisterHandler()
    gpio.registers = registers