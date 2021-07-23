import apiclient

import traceback

class EventHandler:
    def __init__(
            self
        ):

        self.event_log_block = {}
        self.event_faults = {}

    async def check_events(
            self,
            device: dict,
            events: dict,
            state: dict
        ):

        if device["uuid"] not in self.event_log_block:
            self.event_log_block[device["uuid"]] = {}
        

        if device["uuid"] not in self.event_faults:
            self.event_faults[device["uuid"]] = {}

        for event_name, event_info in events.items():
            # Check type
            if event_info["type"] == "fault":
                # Check trigger variable
                if event_info["value"] not in state:
                    if not self.event_log_block[device["uuid"]].get(event_name):
                        await apiclient.messenger.send(
                            "error",
                            {
                                "type": "InvalidEvent",
                                "message": f"Event {event_name} is misconfigured - variable {event_info['value']} does not exist."
                            }
                        )
                        self.event_log_block[device["uuid"]][event_name] = True
                        continue

                value = state[event_info["value"]]

                # Check comparison
                result = await self.compare(
                    value,
                    event_info["comparison"],
                    event_info["threshold"],
                    device,
                    event_name
                )

                if result:
                    # Fault fired
                    if not self.event_faults[device["uuid"]].get(event_name):
                        await apiclient.messenger.send(
                            "fault",
                            {
                                "device": device["name"],
                                "device-uuid": device["uuid"],
                                "description": f"{event_info['value']}: {value} {event_info['comparison']} {event_info['threshold']}",
                                "event": event_name
                            },
                            "device",
                            device["uuid"]
                        )
                        self.event_faults[device["uuid"]][event_name] = True
                    
                elif result is not None:
                    # No error, just not a fault
                    # Reset error log & fault log
                    self.event_faults[device["uuid"]][event_name] = False
                    self.event_log_block[device["uuid"]][event_name] = False

                else:
                    # An error occurred
                    # Only reset fault log
                    self.event_faults[device["uuid"]][event_name] = False
        
    async def compare(
            self,
            value,
            comparison: str,
            threshold,
            device: dict,
            event_name: str
        ):

        if comparison not in apiclient.utils.compare.comparisons:
            if not self.event_log_block[device["uuid"]].get(event_name):
                await apiclient.messenger.send(
                    "error",
                    {
                        "type": "InvalidEvent",
                        "message": f"Event {event_name} is misconfigured - comparison {comparison} does not exist"
                    }
                )
                self.event_log_block[device["uuid"]][event_name] = True

            return None

        try:
            return apiclient.utils.compare.comparisons[comparison](value, threshold)

        except:
            if not self.event_log_block[device["uuid"]].get(event_name):
                await apiclient.messenger.send(
                    "error",
                    {
                        "type": "InvalidEvent",
                        "message": f"Event {event_name} is misconfigured - comparison failed, incompatible types?"
                    }
                )
                traceback.print_exc()
                self.event_log_block[device["uuid"]][event_name] = True

            return None
