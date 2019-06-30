# -*- coding: utf-8 -*-

import json
import logging

import websockets

from .exceptions import ShinkeiResumeWS, ShinkeiWSClosed, ShinkeiWSException
from .keepalive import KeepAlivePls

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
        ws = await websockets.connect(dns, klass=cls)

        ws.client = client
        #  ws.bot = client.bot
        ws.password = client.password
        ws.client_id = client.id
        ws.app_id = client.app_id
        ws.reconnect = reconnect

        await ws.poll_event()

        await ws.identify()

        await ws.poll_event()

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

        if op == self.OP_READY:
            return

        if op == self.OP_GOODBYE:
            raise ShinkeiResumeWS("Received GOODBYE")

        if op == self.OP_HEARTBEAT_ACK:
            self.keep_alive.ack()
            return

        d = data["d"]

        if op == self.OP_HELLO:
            self.hb_interval = d["heartbeat_interval"] / 1000
            return

        if op == self.OP_INVALID:
            msg = d["error"]

            raise ShinkeiWSException(msg)

        if op == self.OP_DISPATCH:
            listeners = self.client.listeners
            for coro in listeners:
                self.loop.create_task(coro(data))

            return

        log.warning("Unhandled OP %d with payload %s", op, data)

    async def identify(self):
        payload = {
            "op": self.OP_IDENTIFY,
            "d": {
                "client_id": self.client_id,
                "application_id": self.app_id,
                "reconnect": self.reconnect,
                "auth": self.password
            }
        }
        log.warning("Sending IDENTIFY payload")
        return await self.send_json(payload)

    async def send_metadata(self, data, *, target, nonce=None):
        payload = {
            "op": self.OP_DISPATCH,
            "d": {
                "nonce": nonce,
                "target": target.to_json(),
                "sender": self.client_id,
                "payload": data,
            },
            "t": "SEND"
        }
        log.debug("Dispatching SEND with payload %s", payload)
        return await self.send_json(payload)

    async def recv_json(self):
        return json.loads(await self.recv())

    async def send_json(self, data):
        log.debug("Sending payload %s", data)
        return await self.send(json.dumps(data))
