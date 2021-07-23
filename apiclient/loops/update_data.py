import apiclient
import gpio
import asyncio

import time

class UpdateDataLoop:
    def __init__(
            self
        ):

        self.name = "update_data"

        self.delay = 3

        self.lenience = 10


        self.devices = {}

    async def run(
            self
        ):

        # Get the node
        node = await apiclient.requests.get(
            "settings/get/node",
            {
                "node": apiclient.config.node_uuid
            }
        )

        apiclient.data.node_name = node["name"]
        apiclient.data.node_uuid = node["uuid"]

        # Check that each device exists
        for device_uuid in node["devices"]:
            if device_uuid not in self.devices:
                device = await apiclient.requests.get(
                    "settings/get/device",
                    {
                        "device": device_uuid
                    }
                )

                self.devices[device_uuid] = {
                    "uuid": device_uuid,
                    "last_updated": 0,
                    "result_cache": None,
                    "events": {},
                    "device_info_updated": 0,
                    "device_object": create_device(device),
                    "device_info": device,
                    "task": None
                }
                apiclient.utils.logger.log("info", f"Registered device {device_uuid}")

        # Iterate over each device, check if it should be updated
        for device_uuid, device in self.devices.items():
            # Check device info
            if device["device_info_updated"] < time.time() - apiclient.config.delays["device_info_refresh"]:
                # Get device info again
                info = await apiclient.requests.get(
                    "settings/get/device",
                    {
                        "device": device_uuid
                    }
                )

                # Check if config changed
                if info["config"] != device["device_info"]["config"]:
                    # Create a new device object
                    del self.devices[device_uuid]["device_object"]

                    self.devices[device_uuid]["device_object"] = create_device(device["device_info"])
                    apiclient.utils.logger.log("info", f"Config changed for {device_uuid} - created new GPIO object")

                apiclient.utils.logger.log("info", f"Refreshed device info for device {device_uuid}")

                device["device_info_updated"] = time.time()

            # Check if info should be updated
            if device["last_updated"] < time.time() - device["device_info"]["polling_rate"]:
                # Refresh device data
                if device["task"] is not None:
                    if not device["task"].done():
                        # Don't continue
                        apiclient.utils.logger.log("warn", f"Device {device['device_info']['name']}'s data task is still running, skipping")
                        continue

                device["task"] = asyncio.get_event_loop().create_task(
                    apiclient.utils.errorhandler.wrap(
                        self.update_device(
                            device_uuid
                        )
                    )
                )

    async def update_device(
            self,
            device_uuid: str
        ):

        device = self.devices[device_uuid]

        result = await asyncio.get_event_loop().run_in_executor(
            None,
            device["device_object"].api_read
        )

        # Send to API
        await apiclient.requests.put(
            "data/put",
            {
                "device": device["device_info"]["uuid"],
                "data": result
            }
        )

        # Check events
        await apiclient.events.check_events(
            device["device_info"],
            device["device_info"]["events"],
            result
        )

        device["last_updated"] = time.time()
        device["result_cache"] = result




def create_device(
        device_info
    ):

    if device_info["type"] not in devices:
        raise apiclient.classes.exceptions.NotFound(f"Device {device_info['type']} doesn't exist")

    # Create device
    device = devices[device_info["type"]](device_info["config"])

    device.prepare()

    return device

devices = {
    "dht22_sensor": gpio.devices.dht22_sensor.config_create,
    "flood_sensor": gpio.devices.flood_sensor.config_create
}