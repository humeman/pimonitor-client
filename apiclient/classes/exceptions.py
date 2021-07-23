class APIError(Exception):
    pass

class APIOffline(Exception):
    pass

class RequestError(Exception):
    pass

class EmptyResponse(Exception):
    pass

class NotFound(Exception):
    pass

class InitError(Exception):
    pass

class SendError(Exception):
    pass