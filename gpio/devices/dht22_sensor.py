from gpio.classes import GPIODevice
from gpio.utils import exceptions

from typing import Iterable
import Adafruit_DHT
import time

def config_create(config):
    return DHT22Sensor(
        {
            "data": config["data_pin"]
        }
    )

class DHT22Sensor(GPIODevice):
    def __init__(
            self,
            pins: dict
        ) -> None:

        super(DHT22Sensor, self).__init__(
            "dht22",
            ["data"],
            pins,
            False
        )

        #self.sensor = adafruit_dht.DHT22(self.pins["data"])

        self.pin_types = {
        }

        self.latest = {
            "temp": None,
            "humidity": None,
            "updated": -1
        }

    def read(
            self,
            return_fahrenheit: bool = True,
            auto_retry: bool = True
        ) -> Iterable[int]:
        """
        Reads the output of the DHT22 sensor.

        Returns True if there's water.

        Parameters:
            return_fahrenheit (bool): Returns fahrenheit
                instead of celsius if true

        Returns:
            temperature (int) - F or C, depending on args
            humidity (int) - 0 to 100
        """
        
        cycles = 0
        while cycles < 3:
            try:
                humidity, temp_raw = Adafruit_DHT.read_retry(22, self.pins["data"], retries = 15)

                if return_fahrenheit:
                    temp = (temp_raw * 9 / 5) + 32

                else:
                    temp = temp_raw

                # Update cached result
                self.latest = {
                    "temp": temp_raw,
                    "humidity": humidity,
                    "updated": int(time.time())
                }

                return temp, humidity

            except Exception as e:
                cycles += 1

                # Reraise if we shouldn't handle this
                if not auto_retry:
                    raise e

        raise exceptions.ReadError(f"Max retry amount of {cycles} reached")

    def api_read(
            self
        ):
        """
        Returns an API-friendly reading.
        """
        data = self.read()

        return {
            "temperature": data[0],
            "humidity": data[1],
            "valid": True
        }