import apiclient

import asyncio
import time

async def wait_for_connect(
        kill: bool = False,
        reason: str = "Not specified"
    ):

    start = time.time()
    fails = 0

    # Holds everything until API connection is established.

    apiclient.utils.logger.log("api", "Holding until API connection is established...", bold = True)

    # Make sure loops are cancelled
    if kill:
        apiclient.utils.logger.log_step("Pausing loops...", "blue")

        # Tell loop handler not to run
        apiclient.loops.pause = True

        for loop in apiclient.loops.loops:
            if loop.task is not None:
                if not loop.task.done():
                    try:
                        loop.task.cancel()

                    except:
                        apiclient.utils.logger.log("warn", f"Failed to cancel loop {loop.name}", "yellow")

                    else:
                        apiclient.utils.logger.log_step(f"Cancelled loop {loop.name}", "blue")

            # Don't log lenience - tell it we already have.
            loop.logs["lenience"] = True

        # *try* to alert. Tell messenger not to contact API first, and ignore errors (could be complete wifi outage)
        await apiclient.messenger.send(
            "pause",
            {
                "reason": reason
            },
            ignore_errors = True,
            dont_refresh = True
        )

    # Start waiting
    while True:
        try:
            await apiclient.requests.get(
                "/status"
            )

        except Exception as e:
            fails += 1

        else: 
            break

        await asyncio.sleep(1)


    # Connection re-established
    apiclient.utils.logger.log_step(f"API connection established after {fails} attempts, {int(time.time() - start)} seconds.", "blue")

    apiclient.requests.online = True

    apiclient.utils.logger.log_step("Starting loops...", "blue")
    apiclient.loops.pause = False

    # Log if this was a kill
    if kill:
        await apiclient.messenger.send(
            "unpause",
            {
                "reason": "API connection reestablished."
            }
        )

async def shutdown(
        reason
    ):
    if not apiclient.requests.online:
        return # Don't run twice

    # Set API offline flag
    apiclient.requests.online = False

    # Log
    apiclient.utils.logger.log("error", f"API has gone offline: {reason}, shutting down", bold = True)

    # Shut down
    await wait_for_connect(
        True,
        f"API request failed: {reason}"
    )
