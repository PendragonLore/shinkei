import aiohttp

class ShinkeiException(Exception): ...


class ShinkeiHTTPException(ShinkeiException):
    request: aiohttp.ClientResponse
    code: int
    message: str

    def __init__(self, request: aiohttp.ClientResponse, code: int, message: str) -> None: ...


class ShinkeiWSException(ShinkeiException):
    message: str

    def __init__(self, message: str) -> None: ...


class ShinkeiResumeWS(ShinkeiException):
    message: str

    def __init__(self, message: str) -> None: ...

class ShinkeiWSClosed(ShinkeiException):
    code: int
    message: str

    def __init__(self, message: str, code: int) -> None: ...
