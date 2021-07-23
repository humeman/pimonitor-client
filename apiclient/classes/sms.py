import apiclient
import aiohttp

import time

class SMSHandler:
    def __init__(
            self
        ):

        self.messages = {
            "exception": {
                "toggle": "exception",
                "require_device": False
            },
            "fault": {
                "toggle": "fault",
                "require_device": True
            },
            "start": {
                "toggle": "start",
                "require_device": False
            },
            "stop": {
                "toggle": "stop",
                "require_device": False
            },
            "error": {
                "toggle": "error",
                "require_device": False
            },
            "pause": {
                "toggle": "pause",
                "require_device": False
            },
            "unpause": {
                "toggle": "unpause",
                "require_device": False
            }
        }

        self.last_reload = 0

        self.twilio_client = None

        self.cache = {}

    async def refresh(
            self
        ):

        # Get exc formats
        settings = await apiclient.requests.get(
            "settings/get"
        )

        # Get twilio info
        self.twilio = {
            "sid": settings["twilio_sid"],
            "token": settings["twilio_token"],
            "from": settings["twilio_from"]
        }

        # Kill some cache
        min_time = time.time() - apiclient.config.delays["phone_cache_max"]
        for device, data in self.cache.items():
            for name, phones in data.items():
                if phones["__stored_at__"] < min_time:
                    del self.cache[device][name]
                    apiclient.utils.logger.log("info", f"Purged phone cache for {device} -> {name}")

    async def send(
            self,
            message_type: str,
            message: str,
            device_type: str = None, # "node" or "device"
            device: str = None, # UUID of above
            dont_refresh: bool = False
        ):

        if self.last_reload < time.time() - 60:
            # Reload every 60 seconds
            if dont_refresh:
                if not hasattr(self, "twilio"):
                    # Raise error, can't ignore since we never got it at all
                    raise apiclient.classes.exceptions.SendError(f"Can't skip refresh - data not retrieved yet")

            else:
                await self.refresh()

        # Get message data
        m_data = self.messages[message_type]

        if m_data["require_device"]:
            if device is None:
                raise Exception(f"Device cannot be None for this request type")

            if dont_refresh:
                if device not in self.cache:
                    apiclient.utils.logger.log("warn", "Can't send, this device isn't cached & no refresh is enabled")
                    return # Can't send

                cache = self.cache[device]

                if m_data["toggle"] not in cache:
                    apiclient.utils.logger.log("warn", "Can't send, this toggle isn't cached & no refresh is enabled")
                    return

                phones = cache[m_data["toggle"]]

                if phones["__stored_at__"] < time.time() - apiclient.config.delays["phone_cache_max"]:
                    apiclient.utils.logger.log("warn", "Can't send, this device's cache is too old")
                    del self.cache[device][m_data["toggle"]]
                    return
                
            else:    
                phones = await apiclient.requests.get(
                    "settings/get/matching_phones",
                    {
                        device_type: device,
                        "toggle": m_data["toggle"]
                    }
                )

                # Cache it
                if device not in self.cache:
                    self.cache[device] = {}

                self.cache[device][m_data["toggle"]] = {
                    **phones,
                    "__stored_at__": int(time.time())
                }

        else:
            # Get all phones
            phones = await apiclient.requests.get(
                "settings/get/matching_phones",
                {
                    "toggle": m_data["toggle"]
                }
            )

        for uuid, phone in phones.items():
            await self.twilio_send(
                phone["number"],
                message[:140]
            )

    async def twilio_send(
            self,
            number: str,
            message: str
        ):

        try:
            async with aiohttp.ClientSession(
                    auth = aiohttp.BasicAuth(
                        login = self.twilio['sid'], 
                        password = self.twilio['token']
                    )
                ) as session:
                    await session.post(
                        f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio['sid']}/Messages.json",
                        data = {'From': self.twilio['from'], 'To': number, 'Body': message})

        except:
            raise apiclient.classes.exceptions.SendError("Failed to send twilio message")