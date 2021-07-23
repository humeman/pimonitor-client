import apiclient

import traceback

async def wrap(
        function,
        on_error = None,
        ignore: list = []
    ):

    try:
        await function

    except Exception as e:
        # Ignore any ignored errors
        if type(e) in ignore:
            return

        if type(e) == apiclient.classes.exceptions.APIOffline:
            return

        # Log in console
        apiclient.utils.logger.log("error", f"An exception occurred!", bold = True)
        apiclient.utils.logger.log_long(traceback.format_exc(), "red", True, True)

        # Log over web
        try:
            await apiclient.messenger.send(
                "exception",
                {
                    "exception": f"{str(type(e))}",
                    "message": f"{str(e)}",
                    "function": function.__name__,
                    "traceback": traceback.format_exc()[:900]
                },
                ignore_errors = True
            )

        except:
            apiclient.utils.logger.log("error", f"Failed to log traceback!", bold = True)
            apiclient.utils.logger.log_long(traceback.format_exc(), "red", True, True)

        if on_error is not None:
            await wrap(
                on_error(e)
            )
    