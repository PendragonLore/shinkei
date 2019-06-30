import json
import logging
import traceback

import websockets

from .exceptions import ShinkeiWSException
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

    async def recv_json(self):
        return json.loads(await self.recv())

    async def send_json(self, data):
        log.debug("Sending payload %s", data)
        return await self.send(json.dumps(data))

    async def identify(self):
        return await self.send_json({
            "op": self.OP_IDENTIFY,
            "d": {
                "client_id": self.client_id,
                "application_id": self.app_id,
                "reconnect": self.reconnect,
                "auth": self.password
            }
        })

    @classmethod
    async def create(cls, client, dns, reconnect):
        ws = await websockets.connect(dns, klass=cls)

        ws.client = client
        #  ws.bot = client.bot
        ws.password = client.password
        ws.client_id = client.id
        ws.app_id = client.app_id
        ws.reconnect = reconnect

        heartbeat_payload = await ws.recv_json()

        ws.hb_interval = heartbeat_payload["d"]["heartbeat_interval"] / 1000
        ws._poll_task = ws.loop.create_task(ws.poll_data())

        await ws.identify()

        ws.keep_alive = KeepAlivePls(ws=ws)
        ws.keep_alive.start()

        return ws

    async def parse_payload(self, data):
        op = data["op"]

        if op == self.OP_GOODBYE:
            if not self.reconnect:
                logging.info("Received GOODBYE payload, disconnecting.")
                return await self.client.close()
            raise NotImplementedError("Reconnection logic not implemented yet.")

        if op in {self.OP_READY, self.OP_HELLO}:
            return

        d = data["d"]

        if op == self.OP_HEARTBEAT_ACK:
            if not d["client_id"] == self.client_id:
                raise ShinkeiWSException("Heartbeat received did not have the same client id as the gateway. "
                                         "(local: {0} from heartbeat: {1})".format(self.client_id, d["client_id"]))
            self.keep_alive.ack()
            return

        if op == self.OP_INVALID:
            msg = d["error"]

            raise ShinkeiWSException(msg)

        if op == self.OP_DISPATCH:
            listeners = self.client.listeners
            for coro in listeners:
                self.loop.create_task(coro(data))

            return

    async def send_metadata(self, data, *, target, nonce=None):
        return await self.send_json({
            "op": self.OP_DISPATCH,
            "d": {
                "nonce": nonce,
                "target": target.to_json(),
                "sender": self.client_id,
                "payload": data,
            },
            "t": "SEND"
        })

    async def poll_data(self):
        while True:
            data = await self.recv_json()

            log.debug("Received payload %s", data)

            try:
                await self.parse_payload(data)
            except Exception:
                traceback.print_exc()
