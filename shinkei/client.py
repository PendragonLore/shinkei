# -*- coding: utf-8 -*-

import asyncio
import inspect
import uuid

import aiohttp
from yarl import URL

from .exceptions import ShinkeiHTTPException
from .gateway import WSClient
from .objects import Version


class Client:
    __slots__ = (
        "loop",
        "password",
        "id",
        "app_id",
        "session",
        "rest_uri",
        "version", "_ws",
        "schema_map",
        "bot"
    )

    listeners = []

    def __init__(self):
        self.password: str
        self.id: str
        self.app_id: str

        self._ws: WSClient
        self.loop: asyncio.AbstractEventLoop
        self.session: aiohttp.ClientSession

        self.schema_map = {"singyeong": "ws", "ssingyeong": "wss"}

    @classmethod
    async def connect(cls, dns, rest_dns, application_id, client_id=None, password=None, *, reconnect=True,
                      session=None, loop=None):
        self = cls()

        self.loop = loop or asyncio.get_event_loop()

        self.password = password
        self.id = client_id or uuid.uuid4().hex
        self.app_id = application_id

        self.session = session or aiohttp.ClientSession()

        ws_url = URL(dns).with_query("encoding=json") / "gateway" / "websocket"
        scheme = self.schema_map.get(ws_url.scheme, ws_url.scheme)

        self.rest_uri = URL(rest_dns) / "api"

        self.version = await self._fetch_version()

        self.rest_uri = self.rest_uri / self.version.api

        self._ws = await WSClient.create(self, ws_url.with_scheme(scheme).human_repr(), reconnect=reconnect)

        return self

    async def close(self):
        await self.session.close()
        self._ws._poll_task.cancel()
        self._ws.keep_alive.stop()
        await self._ws.close(1000)

    async def _fetch_version(self):
        async with self.session.get(self.rest_uri / "version") as request:
            if not request.status == 200:
                raise ShinkeiHTTPException(request, request.status,
                                           f"Was not able to fetch version info ({request.status} {request.reason})")
            return Version(data=await request.json())

    async def discover(self, tags):
        async with self.session.get(self.rest_uri / "discovery" / "tags", params={"q": str(tags)},
                                    headers={"Authorization": str(self.password)}) as request:
            if not request.status == 200:
                raise ShinkeiHTTPException(request, request.status, "Was not able to fetch application id by tags.")

            return (await request.json())["result"]

    async def send(self, data, *, target, nonce=None):
        return await self._ws.send_metadata(data, target=target, nonce=nonce)

    @classmethod
    def listen(cls):
        def wrapper(func):
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Callback must be a coroutine.")
            cls.listeners.append(func)

            return func

        return wrapper
