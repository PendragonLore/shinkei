# -*- coding: utf-8 -*-

import json
import logging

import websockets

from .exceptions import ShinkeiResumeWS, ShinkeiWSClosed, ShinkeiWSException
from .keepalive import KeepAlivePls
from .objects import MetadataPayload

log = logging.getLogger(__name__)


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
    async def create(cls, client, dns, reconnect):
        ws = await websockets.connect(dns, create_protocol=cls)

        ws.client = client
        ws.password = client.password
        ws.client_id = client.id
        ws.app_id = client.app_id
        ws.tags = client.tags
        ws.reconnect = reconnect

        # HELLO payload
        await ws.poll_event()

        await ws.identify()

        ws.keep_alive = KeepAlivePls(ws=ws)
        ws.keep_alive.start()

        return ws

    async def poll_event(self):
        try:
            data = await self.recv_json()
            log.debug("Received payload %s", data)
            await self.parse_payload(data)
        except websockets.exceptions.ConnectionClosed as exc:
            if exc.code not in {1000, 4004, 4010, 4011}:
                raise ShinkeiResumeWS(f"Disconnected with code {exc.code}, trying to reconnect.")
            else:
                raise ShinkeiWSClosed(f"Disconnected with code {exc.code}.", exc.code)

    async def parse_payload(self, data):
        op = data["op"]

        if op == self.OP_GOODBYE:
            raise ShinkeiResumeWS("Received GOODBYE")

        if op == self.OP_HEARTBEAT_ACK:
            self.keep_alive.ack()
            return

        d = data["d"]

        if op == self.OP_HELLO:
            self.hb_interval = d["heartbeat_interval"] / 1000
            return

        if op == self.OP_READY:
            self.client.restricted = d["restricted"]
            cache = self.client._internal_cache
            if cache:
                log.info("Refreshing metadata, probably due to a reconnect (%d entries)", len(cache))
                for payload in cache:
                    await self.update_metadata(payload, cache=False)
            return

        if op == self.OP_INVALID:
            msg = d["error"]

            raise ShinkeiWSException(msg)

        if op == self.OP_DISPATCH:
            listeners = self.client.listeners
            for coro in listeners:
                self.loop.create_task(coro(MetadataPayload(d)))

            return

        log.warning("Unhandled OP %d with payload %s", op, data)

    async def identify(self):
        payload = {
            "op": self.OP_IDENTIFY,
            "d": {
                "client_id": self.client_id,
                "application_id": self.app_id,
                "reconnect": self.reconnect,
                "tags": self.tags
            }
        }
        if self.password:
            payload["auth"] = self.password
        log.info("Sending IDENTIFY payload")
        await self.send_json(payload)

        await self.poll_event()

    async def send_metadata(self, data, *, target, nonce=None):
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
