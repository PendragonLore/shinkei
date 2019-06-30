# -*- coding: utf-8 -*-


class ShinkeiException(Exception):
    pass


class ShinkeiHTTPException(ShinkeiException):
    def __init__(self, request, code, message):
        self.request = request
        self.code = code
        self.message = message

        super().__init__(message)


class ShinkeiWSException(ShinkeiException):
    def __init__(self, message):
        self.message = message

        super().__init__(message)


class ShinkeiResumeWS(ShinkeiException):
    pass


class ShinkeiWSClosed(ShinkeiException):
    def __init__(self, message, code):
        self.code = code
        self.message = message

        super().__init__(message)
