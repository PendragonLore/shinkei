# -*- coding: utf-8 -*-


class ShinkeiException(Exception):
    """Base exception for this library.

    All following exceptions inherit from this."""


class ShinkeiHTTPException(ShinkeiException):
    """The HTTP exception for this library.

    Attributes
    ----------
    request: :class:`aiohttp.ClientResponse`
        The failed request.
    code: :class:`int`
        The request status code.
    message: :class:`str`
        A error message."""
    def __init__(self, request, code, message):
        self.request = request
        self.code = code
        self.message = message

        super().__init__(message)


class ShinkeiWSException(ShinkeiException):
    """The WebSocket exception for this library.

    Attributes
    ----------
    message: :class:`str`
        A error message."""
    def __init__(self, message):
        self.message = message

        super().__init__(message)


class ShinkeiResumeWS(ShinkeiException):
    """An internal exception raised when the WebSocket has been disconnected but can resume."""


class ShinkeiWSClosed(ShinkeiException):
    """An internal exception raised when the WebSocket has been disconnected and can't resume.

    Attributes
    ----------
    code: :class:`int`
        The WebSocket status code.
    message: :class:`str`
        A error message."""
    def __init__(self, message, code):
        self.code = code
        self.message = message

        super().__init__(message)
