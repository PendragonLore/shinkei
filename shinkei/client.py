# -*- coding: utf-8 -*-

import asyncio
import inspect
import logging
import traceback
import uuid

import aiohttp
import websockets
from yarl import URL

from .backoff import ExponentialBackoff
from .exceptions import ShinkeiHTTPException
from .gateway import ShinkeiResumeWS, ShinkeiWSClosed, WSClient
from .objects import Version

log = logging.getLogger(__name__)


class Client:
    __slots__ = (
        "password",
        "id",
        "loop",
        "app_id",
        "session",
        "rest_uri",
        "ws_url",
        "version",
        "reconnect",
        "_ws",
        "schema_map",
        "_task"
    )

    listeners = []

    def __init__(self):
        self.schema_map = {"singyeong": "ws", "ssingyeong": "wss"}

    @classmethod
    async def _connect(cls, dns, rest_dns, application_id, client_id=None, password=None, *, reconnect=True,
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

        self.ws_url = ws_url.with_scheme(scheme)
        self.reconnect = reconnect

        coro = WSClient.create(self, self.ws_url.human_repr(), reconnect=self.reconnect)
        self._ws = await asyncio.wait_for(coro, timeout=30, loop=self.loop)

        self._task = self.loop.create_task(self._poll_data())

        return self

    async def close(self):
        await self.session.close()
        self._ws.keep_alive.stop()
        self._task.cancel()
        await self._ws.close(1000)

    async def _fetch_version(self):
        async with self.session.get(self.rest_uri / "version") as request:
            if not request.status == 200:
                raise ShinkeiHTTPException(request, request.status,
                                           f"Was not able to fetch version info ({request.status} {request.reason})")
            return Version(data=await request.json())

    async def discover(self, tags):
        raise NotImplementedError()

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

    async def _poll_data(self):
        backoff = ExponentialBackoff()

        while True:
            try:
                await self._ws.poll_event()
            except ShinkeiResumeWS:
                log.info("GOODBYE received, trying to reconnect.")
                coro = WSClient.create(self, self.ws_url.human_repr(), reconnect=self.reconnect)

                self._ws = await asyncio.wait_for(coro, timeout=30, loop=self.loop)
            except asyncio.CancelledError:
                raise
            except (OSError,
                    asyncio.TimeoutError,
                    websockets.InvalidHandshake,
                    websockets.WebSocketProtocolError,
                    ShinkeiWSClosed) as exc:
                if not self.reconnect:
                    if isinstance(exc, ShinkeiWSClosed) and exc.code == 1000:
                        return
                    await self.close()
                    traceback.print_exc()
                    raise

                if isinstance(exc, ShinkeiWSClosed):
                    if not exc.code == 1000:
                        await self.close()
                        traceback.print_exc()
                        raise
                    return

                delay = backoff.delay()

                log.debug("Trying to reconnect in %.2fs.", delay)

                await asyncio.sleep(delay)
            except Exception:
                traceback.print_exc()


class _ClientMixin:
    __slots__ = ("_args", "_kwargs", "_client")

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

        self._client = None

    def __await__(self):
        return Client._connect(*self._args, **self._kwargs).__await__()

    async def __aenter__(self):
        self._client = await Client._connect(*self._args, **self._kwargs)

        return self._client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.close()
