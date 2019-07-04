# -*- coding: utf-8 -*-


class Version:
    """An object representing the API and singyeong version.

    Attributes
    ----------
    api: :class:`str`
        The API version, in ``vN`` format.
    singyeong: :class:`str`
        The singyeong version, in ``x.y.z`` format."""
    __slots__ = ("api", "singyeong")

    def __init__(self, data):
        self.api = data["api"]
        self.singyeong = data["singyeong"]

    def __repr__(self):
        return "<Version api={0.api} singyeong={0.singyeong}>".format(self)


class MetadataPayload:
    """An object representing a payload of data received from a client.

    Attributes
    ----------
    sender: :class:`str`
        The ID of the client which sent the payload.
    nonce
        A unique nonce used to identify the payload.
    payload: Union[:class:`str`, :class:`int`, :class:`float`, :class:`list`, :class:`dict`]
        The payload."""
    __slots__ = ("sender", "nonce", "payload")

    def __init__(self, data):
        self.sender = data["sender"]
        self.nonce = data["nonce"]

        self.payload = data["payload"]

    def __repr__(self):
        return "<MetadataPayload sender={0.sender!r} nonce={0.nonce}>".format(self)
