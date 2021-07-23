from typing import Callable

from gpio.utils import (
        exceptions
    )

class RegisterHandler:
    def __init__(
            self
        ) -> None:

        self.registers = {
            "ready": {
                "called": None,
                "functions": []
            }
        }

    def run_on(
            self,
            function: Callable,
            event: str
        ) -> None:
        """
        Makes the RegisterHandler run the specified
        function on the specified event.

        No arguments will be passed to the function.

        Parameters:
            function (Callable): Function to call
            event (str): Event to call on
                ready - When initialization is done
        """

        if event not in self.registers:
            raise exceptions.InvalidEvent(f"Event {event} doesn't exist")

        if self.registers[event]["called"]:
            raise exceptions.InvalidEvent(f"One-time event {event} has already been called")

        self.registers[event]["functions"].append(function)

    def call(
            self,
            event: str
        ) -> None:
        """
        Fires an event.

        Parameters:
            event (str)
        """
        if event not in self.registers:
            raise exceptions.InvalidEvent(f"Event {event} doesn't exist")

        if self.registers[event]["called"]:
            raise exceptions.InvalidEvent(f"One-time event {event} has already been called")

        for function in self.registers[event]["functions"]:
            function()

        if self.registers[event]["called"] is not None:
            self.registers[event]["called"] = True
        