# -*- coding: utf-8 -*-

import logging

import websockets

from .exceptions import ShinkeiResumeWS, ShinkeiWSClosed, ShinkeiWSException
from .keepalive import KeepAlivePls
from .objects import MetadataPayload

try:
    import ujson as json
except ImportError:
    import json

log = logging.getLogger(__name__)


# noinspection PyProtectedMember
class WSClient(websockets.WebSocketClientProtocol):
    OP_HELLO = 0
    OP_IDENTIFY = 1
    OP_READY = 2
    OP_INVALID = 3
    OP_DISPATCH = 4
    OP_HEARTBEAT = 5
    OP_HEARTBEAT_ACK = 6
    OP_GOODBYE = 7

    @classmethod
    async def create(cls, client, url, *, reconnect):
        ws = await websockets.connect(url.human_repr(), create_protocol=cls, loop=client.loop)

        ws.set_attrs(ws, client, reconnect=reconnect)

        ws._dispatch("connect")

        # HELLO payload
        await ws.poll_event()

        await ws.identify()

        ws.keep_alive = KeepAlivePls(ws=ws)
        ws.keep_alive.start()

        return ws

    @staticmethod
    def set_attrs(ws, client, *, reconnect):
        ws.client = client
        ws.auth = client.auth
        ws.client_id = client.id
        ws.app_id = client.app_id
        ws.tags = client.tags
        ws.reconnect = reconnect

    async def poll_event(self):
        try:
            data = await self.recv_json()
            log.debug("Received payload %s", data)
            await self.parse_payload(data)
        except websockets.exceptions.ConnectionClosed as exc:
            if exc.code not in {1000, 4004, 4010, 4011}:
                raise ShinkeiResumeWS(f"Disconnected with code {exc.code}, trying to reconnect.")

            raise ShinkeiWSClosed(f"Disconnected with code {exc.code}.", exc.code)

    async def parse_payload(self, data):
        self._dispatch("raw_socket", data)
        op = data["op"]

        if op == self.OP_HEARTBEAT_ACK:
            self.keep_alive.ack()
            return

        d = data["d"]

        if op == self.OP_HELLO:
            # noinspection PyAttributeOutsideInit
            self.hb_interval = d["heartbeat_interval"] / 1000
            return

        if op == self.OP_GOODBYE:
            raise ShinkeiResumeWS(f"Received GOODBYE (reason: {d.get('reason')})")

        if op == self.OP_READY:
            self._dispatch("ready")
            self.client.restricted = restricted = d["restricted"]
            if restricted:
                log.warning("Client is restricted.")
            cache = self.client._internal_cache
            if cache:
                log.info("Refreshing metadata, probably due to a reconnect (%d entries)", len(cache))
                for payload in cache:
                    await self.update_metadata(payload, cache=False)
            return

        if op == self.OP_INVALID:
            msg = d["error"]
            self._dispatch("error", msg)

            raise ShinkeiWSException(msg)

        if op == self.OP_DISPATCH:
            self._dispatch("data", MetadataPayload(d))

            return

        log.warning("Unhandled OP %d with payload %s", op, data)

    def _dispatch(self, name, *args):
        waiters = self.client._waiters.get(name)
        if waiters:
            removed = []
            for index, (future, check) in enumerate(waiters):
                if future.cancelled():
                    removed.append(index)
                    continue

                try:
                    result = check(*args)
                except Exception as exc:
                    future.set_exception(exc)
                    removed.append(index)
                else:
                    if result:
                        if not args:
                            future.set_result(None)
                        if len(args) == 1:
                            future.set_result(args[0])
                        else:
                            future.set_result(args)
                        removed.append(index)

            if len(removed) == len(waiters):
                self.client._waiters.pop(name)
            else:
                for i in reversed(removed):
                    del waiters[i]

        for handler in self.client.handlers.values():
            for _, coro_name in filter(lambda x: x[0] == name, handler.__shinkei_handlers__):
                self.loop.create_task(getattr(handler, coro_name)(*args))

    async def identify(self):
        payload = {
            "op": self.OP_IDENTIFY,
            "d": {
                "client_id": self.client_id,
                "application_id": self.app_id,
                "reconnect": self.reconnect,
            }
        }
        if self.auth is not None:
            payload["d"]["auth"] = self.auth
        if self.tags is not None:
            # noinspection PyTypeChecker
            payload["d"]["tags"] = self.tags
        log.info("Sending IDENTIFY payload")
        await self.send_json(payload)

        await self.poll_event()

    async def send_metadata(self, data, *, target, nonce=None):
        if self.client.restricted:
            raise ShinkeiWSException("Restricted clients cannot SEND.")
        payload = {
            "op": self.OP_DISPATCH,
            "t": "SEND",
            "d": {
                "nonce": nonce,
                "target": target.to_json(),
                "sender": self.client_id,
                "payload": data,
            },
        }
        return await self.send_json(payload)

    async def broadcast_metadata(self, data, *, target, nonce=None):
        if self.client.restricted:
            raise ShinkeiWSException("Restricted clients cannot BROADCAST.")
        payload = {
            "op": self.OP_DISPATCH,
            "t": "BROADCAST",
            "d": {
                "nonce": nonce,
                "target": target.to_json(),
                "sender": self.client_id,
                "payload": data,
            },
        }
        return await self.send_json(payload)

    async def update_metadata(self, data, *, cache=True):
        payload = {
            "op": self.OP_DISPATCH,
            "t": "UPDATE_METADATA",
            "d": data,
        }
        if cache:
            self.client._internal_cache.append(data)
        return await self.send_json(payload)

    async def recv_json(self):
        return json.loads(await self.recv())

    async def send_json(self, data):
        log.debug("Sending payload %s", data)
        return await self.send(json.dumps(data))
