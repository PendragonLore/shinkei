# -*- coding: utf-8 -*-

import asyncio
import concurrent
import logging
import threading
import time

try:
    import ujson as json
except ImportError:
    import json

log = logging.getLogger(__name__)


class KeepAlivePls(threading.Thread):
    def __init__(self, *args, **kwargs):
        # noinspection PyUnresolvedReferences
        self.ws = kwargs.pop("ws")
        self.interval = self.ws.hb_interval

        super().__init__(*args, **kwargs)

        self.daemon = True
        self.stop_event = threading.Event()
        self._last_ack = time.perf_counter()
        self._last_send = time.perf_counter()
        self.latency = float("inf")

    def run(self):
        data = json.dumps({
            "op": self.ws.OP_HEARTBEAT,
            "d": {"client_id": self.ws.client_id}
        })

        while not self.stop_event.wait(self.interval):
            future = asyncio.run_coroutine_threadsafe(self.ws.send(data), loop=self.ws.loop)
            # noinspection PyBroadException
            try:
                total = 0
                while True:
                    # noinspection PyUnresolvedReferences
                    try:
                        log.debug("Sending heartbeat for client with id %s", self.ws.client_id)
                        future.result(timeout=5)
                        break
                    except concurrent.futures.TimeoutError:
                        total += 5
                        log.warning("Heartbeat blocked for more then %s", total)
            except Exception:
                self.stop()
            else:
                self._last_send = time.perf_counter()

    def stop(self):
        self.stop_event.set()

    def ack(self):
        self._last_ack = time.perf_counter()
        self.latency = self._last_ack - self._last_send
        log.debug("Acked heartbeat for client with id %s", self.ws.client_id)

        if self.latency > 10:
            log.warning("Websocket is %.1fs behind.", self.latency)
