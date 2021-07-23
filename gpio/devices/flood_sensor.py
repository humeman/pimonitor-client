from gpio.classes import GPIODevice

from RPi import GPIO

def config_create(config):
    return FloodSensor(
        {
            "pud": config["pud_pin"]
        }
    )

class FloodSensor(GPIODevice):
    def __init__(
            self,
            pins: dict
        ) -> None:

        super(FloodSensor, self).__init__(
            "flood_sensor",
            ["pud"],
            pins
        )

        self.pin_types = {
            self.pins["pud"]: {
                "type": GPIO.IN,
                "kwargs": {
                    "pull_up_down": GPIO.PUD_UP
                }
            }
        }

    def read(
            self
        ):
        """
        Required debugging alias to sense().
        """
        return self.sense()

    def sense(
            self
        ):
        """
        Reads the output of the flood sensor.

        Returns True if there's water.

        Returns:
            state (bool): Whether or not water
                is detected
        """

        return not GPIO.input(self.pins["pud"])
    
    def api_read(
            self
        ):
        """
        Returns an API-friendly reading.
        """

        return {
            "state": self.sense()
        }