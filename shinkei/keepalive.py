# -*- coding: utf-8 -*-

import asyncio
import concurrent
import json
import logging
import threading

log = logging.getLogger(__name__)


class KeepAlivePls(threading.Thread):
    def __init__(self, *args, **kwargs):
        self.ws = kwargs.pop("ws")
        self.interval = self.ws.hb_interval

        super().__init__(*args, **kwargs)

        self.daemon = True
        self.stop_event = threading.Event()

    def run(self):
        data = json.dumps({
            "op": self.ws.OP_HEARTBEAT,
            "d": {"client_id": self.ws.client_id}
        })

        while not self.stop_event.wait(self.interval):
            future = asyncio.run_coroutine_threadsafe(self.ws.send(data), loop=self.ws.loop)
            try:
                total = 0
                while True:
                    try:
                        log.debug("Sending heartbeat for client with id %s", self.ws.client_id)
                        future.result(timeout=5)
                        break
                    except concurrent.futures.TimeoutError:
                        total += 5
                        log.warning("Heartbeat blocked for more then %s", total)
            except Exception:
                self.stop()

    def stop(self):
        self.stop_event.set()

    def ack(self):
        log.debug("Acked heartbeat for client with id %s", self.ws.client_id)
