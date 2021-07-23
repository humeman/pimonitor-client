
from RPi import GPIO

from gpio.utils import (
        exceptions
    )
import gpio

class GPIODevice:
    def __init__(
            self,
            type: str,
            req_pins: list,
            pins: dict,
            setup_gpio: bool = True
        ) -> None:
        """
        Constructs a GPIODevice.

        This class should be extended by another object.

        Arguments:
            type (str): Device type
            req_pins (list<str>): Required pin names
            pins (dict): Actual pin values
            setup_gpio (bool): Enable/disable auto-GPIO setup
        """
        # Set mode
        self.mode = "BCM"

        # Save the type
        self._type = type

        # Store the required pins into a new pins dict
        self.pins = {x: None for x in req_pins}

        # Transfer in all of the defined pins
        for pin, pin_id in pins.items():
            # Make sure the pin is valid
            if pin not in self.pins:
                raise exceptions.InvalidDevice(f"Pin {pin} is not needed for {self._type}")

            # Store it
            self.pins[pin] = pin_id

        # Make sure every required pin is defined
        for pin, value in self.pins.items():
            if value is None:
                raise exceptions.InvalidDevice(f"Pin {pin} must be defined for {self._type}")

        # Tell module to run this on start
        if setup_gpio:
            print(f"Registered ready event for {self._type}")
            gpio.registers.run_on(self.prepare, "ready")

    def prepare(
            self
        ) -> None:
        """
        Prepares the device for being read while the library
        is being initialized. Called automatically.
        """

        # Make sure GPIO mode is set correctly
        modes = {
            "BCM": GPIO.BCM,
            "BOARD": GPIO.BOARD
        }

        if self.mode not in modes:
            raise exceptions.InvalidDevice(f"GPIO mode {self.mode} does not exist")

        gpio_mode = modes[self.mode]

        if GPIO.getmode() != gpio_mode:
            GPIO.setmode(gpio_mode)

        self.set_pins()

    def set_pins(
            self
        ) -> None:
        """
        Sets up the pins in the RPi GPIO module.
        Must be called after full initialization, since these
        pin types will be set in objects that extend this class.
        """

        for pin_id, info in self.pin_types.items():
            GPIO.setup(pin_id, info["type"], **info["kwargs"])
            print(f"Setup {pin_id} {info['type']}")


class OtherGPIODevice:
    def __init__(
            self,
            type: str
        ) -> None:
        """
        Constructs an OtherDevice.

        This class should be extended by another object.

        Arguments:
            type (str): Device type
        """
        self.type = type




