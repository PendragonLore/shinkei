# -*- coding: utf-8 -*-


class Version:
    __slots__ = ("api", "singyeong")

    def __init__(self, data):
        self.api = data["api"]
        self.singyeong = data["singyeong"]

    def __repr__(self):
        return "<Version api={0.api} singyeong={0.singyeong}>".format(self)


class MetadataPayload:
    __slots__ = ("sender", "nonce", "payload")

    def __init__(self, data):
        self.sender = data["sender"]
        self.nonce = data["nonce"]

        self.payload = data["payload"]
