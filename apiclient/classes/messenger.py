import apiclient

import discordwebhook
import traceback

class Messenger:
    def __init__(
            self
        ):

        self.messages = apiclient.config.messages

    async def prep(
            self
        ):
        # Load up SMS templates from API
        settings = await apiclient.requests.get(
            f"settings/get"
        )

        for message in self.messages:
            if f"{message}_format" not in settings:
                raise apiclient.classes.exceptions.InitError(f"Message {message} has no format in API settings")

            self.messages[message]["sms_format"] = settings[f"{message}_format"]

    async def send_safe(
            self,
            *args,
            **kwargs
        ):

        await apiclient.utils.errorhandler.wrap(
            self.send(
                *args,
                **kwargs
            )
        )

    async def send(
            self,
            message_type: str,
            placeholders: dict,
            device_type: str = None, # node or device
            device: str = None, # UUID of above
            ignore_errors: bool = False,
            dont_refresh: bool = False
        ):

        placeholders = {
            **placeholders,
            "node": apiclient.data.node_name,
            "node-uuid": apiclient.data.node_uuid
        }

        if message_type not in self.messages:
            raise apiclient.classes.exceptions.NotFound(f"Message type {message_type} does not exist")

        msg = self.messages[message_type]
        message = msg["sms_format"]

        # Compile raw placeholders
        for name, value in placeholders.items():
            message = message.replace(f"%{name}%", str(value))

        if msg["console"]:
            # Should never fail - only ignore errors for wifi things
            apiclient.utils.logger.log("msg", message, bold = True)

        if msg["sms"]:
            try:
                await apiclient.sms.send(
                    message_type,
                    message,
                    device_type,
                    device,
                    dont_refresh = dont_refresh
                )

            except Exception as e:
                if ignore_errors:
                    apiclient.utils.logger.log("warn", f"Failed to send SMS message. Ignoring.")

                else:
                    raise e


        if msg["webhook"]:
            webhook = discordwebhook.asyncCreate.Webhook(apiclient.config.webhook_url)

            # Create embed
            try:
                await webhook.send(
                    embed = create_embed(
                        msg["webhook_embed"],
                        placeholders
                    )
                )

            except Exception as e:
                if ignore_errors:
                    apiclient.utils.logger.log("warn", f"Failed to send webhook message. Ignoring.")

                else:
                    raise e
        
def create_embed(
        msg_format,
        placeholders
    ):
    kw = {}

    keys = ["title", "description", "color"]

    for key in keys:
        if key in msg_format:
            if type(msg_format[key]) == str:
                kw[key] = add_placeholders(msg_format[key], placeholders)

            else:
                kw[key] = msg_format[key]

    embed = discordwebhook.asyncCreate.Embed(
        **kw
    )

    if "fields" in msg_format:
        comp = []
        for field in msg_format["fields"]:
            embed.add_field(
                name = add_placeholders(field["name"], placeholders),
                value = add_placeholders(field["value"], placeholders),
                inline = field["inline"] if "inline" in field else False
            )

    return embed

def add_placeholders(
        string,
        placeholders
    ):
    for name, value in placeholders.items():
        string = string.replace(f"%{name}%", str(value))

    return string