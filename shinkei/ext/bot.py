import asyncio

from yarl import URL

from ..api import APIClient
from ..client import Client
from ..gateway import WSClient


class BotWSClient(WSClient):
    @classmethod
    async def create(cls, client, url, *, reconnect):
        ws = await super().create(client, url, reconnect=reconnect)

        ws.bot = client.bot

        return ws

    def _dispatch(self, name, *args):
        self.bot.dispatch(f"shinkei_{name}")


class BotClient(Client):
    @classmethod
    async def _connect(cls, url, rest_url, application_id, client_id, auth=None, *, reconnect=True,
                       session=None, loop=None, tags=None, handlers=None, **kwargs):
        self = cls()

        try:
            self.bot = kwargs.pop("bot")
        except KeyError:
            raise TypeError("bot must always be provided when using BotClient")

        if handlers is not None:
            for handler in handlers:
                self.add_handler(handler)

        self.loop = self.bot.loop

        self.auth = auth
        self.id = client_id
        self.app_id = application_id
        self.tags = tags or []

        ws_url = URL(url).with_query("encoding=json") / "gateway" / "websocket"
        scheme = self.schema_map.get(ws_url.scheme, ws_url.scheme)

        self.ws_url = ws_url.with_scheme(scheme)
        self.reconnect = reconnect

        coro = BotWSClient.create(self, self.ws_url.human_repr(), reconnect=self.reconnect)
        self._ws = await asyncio.wait_for(coro, timeout=20)

        self._rest = await APIClient.create(rest_url, session=session, auth=auth, loop=self.loop)

        self.version = self._rest.version

        self._task = self.loop.create_task(self._poll_data())

        return self

    def add_handler(self, handler):
        raise NotImplementedError("add_handler() cannot be used with BotClient "
                                  "(events are dispatched through bot.dispatch('shinkei_{event_name}'))")

    def remove_handler(self, handler_name):
        raise NotImplementedError("remove_handler() cannot be used with BotClient "
                                  "(events are dispatched through bot.dispatch('shinkei_{event_name}'))")

    async def wait_for(self, event, *, timeout=None, check=None):
        raise NotImplementedError("wait_for() cannot be used with BotClient "
                                  "(use bot.wait_for('shinkei_{event_name}'))")
