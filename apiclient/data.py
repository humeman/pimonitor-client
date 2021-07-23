from . import classes
import apiclient

import gpio

import asyncio

def init(path = "config.yml"):
    apiclient.utils.logger.log(
        "start",
        f"Starting PiMonitor Node v{apiclient.version}",
        bold = True    
    )

    # Config
    apiclient.utils.logger.log_step("Initializing config...", "cyan")
    global config
    config = classes.config.Config(path)

    apiclient.config = config

    asyncio.get_event_loop().run_until_complete(config.load())

    # API handler
    apiclient.utils.logger.log_step("Initializing API handler...", "cyan")
    global requests
    requests = classes.requests.RequestHandler()

    apiclient.requests = requests

    # SMS handler
    apiclient.utils.logger.log_step("Initializing SMS handler...", "cyan")
    global sms
    sms = classes.sms.SMSHandler()

    apiclient.sms = sms

    # Messenger
    apiclient.utils.logger.log_step("Initializing messenger...", "cyan")
    global messenger
    messenger = classes.messenger.Messenger()

    apiclient.messenger = messenger

    # Event handler
    apiclient.utils.logger.log_step("Initializing event handler...", "cyan")
    global events
    events = classes.events.EventHandler()

    apiclient.events = events

    # Loop handler
    apiclient.utils.logger.log_step("Initializing loops...", "cyan")
    global loops
    loops = classes.loops.LoopHandler()

    apiclient.loops = loops

def start():
    # Wait on API
    print()
    asyncio.get_event_loop().run_until_complete(apiclient.utils.apiutils.wait_for_connect())
    print()

    apiclient.utils.logger.log("start", f"Finishing initialization...")
    # Init everything
    apiclient.utils.logger.log_step("Preparing messenger...", "cyan")
    asyncio.get_event_loop().run_until_complete(messenger.prep())

    loops.load()
    apiclient.utils.logger.log_step("Starting loops...", "cyan")
    asyncio.get_event_loop().create_task(loops.start())

    # Check node
    apiclient.utils.logger.log_step("Getting node...", "cyan")
    asyncio.get_event_loop().run_until_complete(
        get_node()
    )
    apiclient.utils.logger.log_step(f"Running as node {node_name} ({node_uuid})", "cyan", bold = True)
    apiclient.utils.logger.log_step("Initialized!", "cyan", bold = True)

    # Log
    asyncio.get_event_loop().create_task(
        apiclient.messenger.send(
            "start",
            {
                "node-uuid": apiclient.config.node_uuid,
                "node": "temp"
            }
        )
    )

    asyncio.get_event_loop().run_forever()

async def get_node():
    node = await apiclient.requests.get(
        "settings/get/node",
        {
            "node": apiclient.config.node_uuid
        }
    )

    global node_name
    node_name = node["name"]
    global node_uuid
    node_uuid = node["uuid"]