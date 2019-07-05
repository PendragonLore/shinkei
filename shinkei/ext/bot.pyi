import asyncio
from typing import Any, List, Optional, Type

import aiohttp

from ..client import Client
from ..gateway import WSClient
from ..handlers import Handler


class BotWSClient(WSClient):
    client: BotClient

    @staticmethod
    def set_attrs(ws: BotWSClient, client: BotClient, *, reconnect: bool) -> None: ...

class BotClient(Client):
    bot: Any

    # noinspection PyMethodOverriding
    @classmethod
    async def _connect(cls: Type[BotClient], url: str, application_id: str, client_id: str,
                       auth: Optional[str] = ..., *, tags: Optional[list] = ..., reconnect: Optional[bool] = ...,
                       session: Optional[aiohttp.ClientSession] = ..., loop: Optional[asyncio.AbstractEventLoop] = ...,
                       handlers: Optional[List[Handler]] = ..., bot: Any, **kwargs) -> BotClient: ...
