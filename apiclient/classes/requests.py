import apiclient

import httpx

class RequestHandler:
    def __init__(
            self
        ):
        """
        Constructs a RequestHandler.

        Will read values from apiclient.config - must be initialized first.
        """

        self.base_url = apiclient.config.api_url

        self.auth = {
            "key": apiclient.config.api_key
        }

        self.online = False

    async def get(
            self,
            url: str,
            args: dict = {},
            local_request: bool = True
        ):

        if local_request:
            args = {
                **args,
                **self.auth
            }

            url = f"{self.base_url}/{url}"

        try:
            r = await self._get(url, args)

        except httpx.HTTPStatusError as e:
            raise apiclient.classes.exceptions.APIError(f"API returned non-200 status code: {e.response.status_code}.")

        except httpx.ConnectError as e:
            # Tell API client to shut down
            if self.online: # Only if just gone offline
                await apiclient.utils.apiutils.shutdown(str(e))

            raise apiclient.classes.exceptions.APIOffline(f"API is offline: {str(e)}")

        except httpx.RequestError as e:
            if self.online:
                await apiclient.utils.apiutils.shutdown(str(e))

            raise apiclient.classes.exceptions.RequestError(f"Failed to send request to API: {str(e)}")

        try:
            data = r.json()

        except:
            raise apiclient.classes.exceptions.EmptyResponse("Request returned no JSON data")

        if local_request:
            if not data["success"]:
                raise apiclient.classes.exceptions.APIError(f"API returned error: {data.get('error')}: {data.get('reason')}")

            return data.get("data")

    async def put(
            self,
            url: str,
            json: dict = {},
            local_request: bool = True
        ):

        if local_request:
            json = {
                **json,
                **self.auth
            }

            url = f"{self.base_url}/{url}"

        try:
            r = await self._put(url, json = json)

        except httpx.HTTPStatusError as e:
            raise apiclient.classes.exceptions.APIError(f"API returned non-200 status code: {e.response.status_code}.")

        except httpx.ConnectError as e:
            # Tell API client to shut down
            await apiclient.utils.apiutils.shutdown(str(e))
            raise apiclient.classes.exceptions.APIOffline(f"API is offline: {str(e)}")

        except httpx.RequestError as e:
            await apiclient.utils.apiutils.shutdown(str(e))
            raise apiclient.classes.exceptions.RequestError(f"Failed to send request to API: {str(e)}")

        try:
            data = r.json()

        except:
            raise apiclient.classes.exceptions.EmptyResponse("Request returned no JSON data")

        if local_request:
            if not data["success"]:
                raise apiclient.classes.exceptions.APIError(f"API returned error: {data.get('error')}: {data.get('reason')}")

            return data.get("data")

    async def post(
            self,
            url: str,
            json: dict = {},
            local_request: bool = True
        ):

        if local_request:
            json = {
                **json,
                **self.auth
            }

            url = f"{self.base_url}/{url}"

        try:
            r = await self._post(url, json = json)

        except httpx.HTTPStatusError as e:
            raise apiclient.classes.exceptions.APIError(f"API returned non-200 status code: {e.response.status_code}.")

        except httpx.ConnectError as e:
            # Tell API client to shut down
            await apiclient.utils.apiutils.shutdown(str(e))
            raise apiclient.classes.exceptions.APIOffline(f"API is offline: {str(e)}")

        except httpx.RequestError as e:
            await apiclient.utils.apiutils.shutdown(str(e))
            raise apiclient.classes.exceptions.RequestError(f"Failed to send request to API: {str(e)}")

        try:
            data = r.json()

        except:
            raise apiclient.classes.exceptions.EmptyResponse("Request returned no JSON data")

        if local_request:
            if not data["success"]:
                raise apiclient.classes.exceptions.APIError(f"API returned error: {data.get('error')}: {data.get('reason')}")

            return data.get("data")

    async def _get(
            self,
            url: str,
            args: dict
        ):
        comp = []
        for name, value in args.items():
            comp.append(f"{name}={value}")

        if len(comp) > 0:
            url += f"?{'&'.join(comp)}"

        async with httpx.AsyncClient() as c:
            return await c.get(url)

    async def _put(
            self,
            url: str,
            json: dict
        ):
        async with httpx.AsyncClient() as c:
            return await c.put(url, json = json)

    async def _post(
            self,
            url: str,
            json: dict
        ):
        async with httpx.AsyncClient() as c:
            return await c.post(url, json = json)

        