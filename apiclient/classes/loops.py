import apiclient

import traceback
import asyncio
import time
import concurrent

class LoopHandler:
    def __init__(
            self
        ):

        self.loops = [
            apiclient.loops.update_data.UpdateDataLoop()
        ]

        self.pause = True # Pause until we have API connection

    def load(
            self
        ):

        for loop in self.loops:
            loop.task = None
            loop.last_run = -1
            loop.errors = 0
            loop.pause_until = None
            self.refresh_logs(loop)

    def refresh_logs(
            self,
            loop
        ):

        loop.logs = {
            "lenience": False  # Loop taking too long to run
        }

    async def start(
            self
        ):

        while True:
            if self.pause:
                await asyncio.sleep(1) # Still don't block
                continue

            # Find which loops need to be run
            for loop in self.loops:
                current_time = time.time()

                # Check loop task
                if loop.task is not None:
                    if not loop.task.done():
                        # Can't run again since it's still running

                        # Loop last run [lenience] seconds ago and isn't finished yet
                        if loop.last_run < current_time - loop.lenience and not loop.logs["lenience"]:
                            await apiclient.messenger.send(
                                "exception",
                                {
                                    "exception": f"Loop {loop.name} has exceeded lenience of {loop.lenience} without completing"
                                }
                            )
                            loop.logs["lenience"] = True
                        
                        continue

                if loop.last_run < current_time - loop.delay:
                    # Loop needs to be run

                    # If loop is paused
                    if loop.pause_until is not None:
                        if loop.pause_until > current_time:
                            continue
                    
                        else:
                            loop.pause_until = None

                    # If loop is errored out
                    if loop.errors >= 3:
                        continue

                    # Try to run it
                    if not self.pause:
                        loop.task = asyncio.get_event_loop().create_task(apiclient.utils.errorhandler.wrap(loop.run(), on_error = lambda *args: self.log_error(str(loop.name), *args), ignore = [concurrent.futures._base.CancelledError]))
                        loop.last_run = current_time

                        loop.logs["lenience"] = False

            await asyncio.sleep(1) # So we don't block everything

    async def log_error(
            self,
            loop_name: str,
            exception: str
        ) -> None:

        # Get traceback
        try:
            raise exception

        except:
            msg = traceback.format_exc()

        # Get loop
        for loop_ in self.loops:
            if loop_.name == loop_name:
                loop = loop_

        # Update error count
        loop.errors += 1

        if loop.errors >= 3:
            await apiclient.messenger.send(
                "error",
                {
                    "type": "Loop paused",
                    "message": f"Loop {loop.name} errored 3 times, so it has been paused. Restart the client to start it again."
                }
            )

        # Pause
        loop.pause_until = int(time.time()) + 60 # Wait for a minute



    