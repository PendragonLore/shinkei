# -*- coding: utf-8 -*-

import asyncio
import inspect
import logging
import traceback

import websockets
from yarl import URL

from .api import APIClient
from .backoff import ExponentialBackoff
from .gateway import ShinkeiResumeWS, ShinkeiWSClosed, WSClient

log = logging.getLogger(__name__)


def connect(*args, **kwargs):
    return _ClientMixin(*args, **kwargs)


class Client:
    listeners = []

    def __init__(self):
        self.restricted = None
        self._closed_event = asyncio.Event()
        self.schema_map = {"singyeong": "ws", "ssingyeong": "wss"}

    @classmethod
    async def _connect(cls, dns, rest_dns, application_id, client_id, password=None, *, reconnect=True,
                       session=None, loop=None, tags=None):
        self = cls()

        self.loop = loop or asyncio.get_event_loop()

        self.password = password
        self.id = client_id
        self.app_id = application_id
        self.tags = tags or []

        self._internal_cache = []

        ws_url = URL(dns).with_query("encoding=json") / "gateway" / "websocket"
        scheme = self.schema_map.get(ws_url.scheme, ws_url.scheme)

        self.ws_url = ws_url.with_scheme(scheme)
        self.reconnect = reconnect

        coro = WSClient.create(self, self.ws_url.human_repr(), reconnect=self.reconnect)
        self._ws = await asyncio.wait_for(coro, timeout=20)

        self._rest = await APIClient.create(rest_dns, session=session, password=password)

        self.version = self._rest.version

        self._task = self.loop.create_task(self._poll_data())

        return self

    @property
    def is_closed(self):
        return self._closed_event.is_set()

    @property
    def latency(self):
        return self._ws.keep_alive.latency

    async def close(self):
        self._closed_event.set()
        if not self._rest.session.closed:
            await self._rest.session.close()
        self._ws.keep_alive.stop()
        await self._ws.close(1000)

    async def send(self, data, *, target, nonce=None):
        return await self._ws.send_metadata(data, target=target, nonce=nonce)

    async def broadcast(self, data, *, target, nonce=None):
        return await self._ws.broadcast_metadata(data, target=target, nonce=nonce)

    async def update_metadata(self, data):
        return await self._ws.update_metadata(data)

    async def proxy_request(self, method, route, application, *, ops):
        return await self._rest.proxy(method, route, application, ops)

    async def discover(self, tags):
        ret = await self._rest.discovery_tags(tags)

        return ret.get("result")

    @classmethod
    def listen(cls):
        def wrapper(func):
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Callback must be a coroutine.")
            cls.listeners.append(func)

            return func

        return wrapper

    async def _do_poll(self):
        try:
            await self._ws.poll_event()
        except ShinkeiResumeWS:
            if not self.reconnect:
                log.info("GOODBYE received, disconnected")
                self._task.cancel()
                await self.close()
                return
            log.info("GOODBYE received, trying to reconnect.")
            coro = WSClient.create(self, self.ws_url.human_repr(), reconnect=self.reconnect)

            self._ws = await asyncio.wait_for(coro, timeout=20.0, loop=self.loop)

    async def _poll_data(self):
        backoff = ExponentialBackoff()

        while True:
            try:
                await self._do_poll()
            except asyncio.CancelledError:
                raise
            except (OSError,
                    ValueError,
                    asyncio.TimeoutError,
                    websockets.InvalidHandshake,
                    websockets.WebSocketProtocolError,
                    ShinkeiWSClosed,
                    websockets.InvalidMessage) as exc:
                if not self.reconnect:
                    await self.close()
                    if isinstance(exc, ShinkeiWSClosed) and exc.code == 1000:
                        log.info("Websocket closed successfully.")
                        return
                    log.warning("Websocket closed forcefully.")
                    traceback.print_exc()
                    raise

                if self.is_closed:
                    log.info("Websocket closed successfully.")
                    return

                if isinstance(exc, ShinkeiWSClosed):
                    if not exc.code == 1000:
                        await self.close()
                        log.warning("Websocket closed forcefully.")
                        traceback.print_exc()
                        raise

                delay = backoff.delay()
                log.debug("Trying to reconnect in %.2fs.", delay)
                await asyncio.sleep(delay, loop=self.loop)
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
