from typing import Optional, List, Any, Type

import aiohttp
import asyncio

from ..client import Client
from ..handlers import Handler


class BotClient(Client):
    bot: Any

    async def _connect(cls: Type[BotClient], url: str, application_id: str, client_id: str,
                       auth: Optional[str] = ..., *, tags: Optional[list] = ..., reconnect: Optional[bool] = ...,
                       session: Optional[aiohttp.ClientSession] = ..., loop: Optional[asyncio.AbstractEventLoop] = ...,
                       handlers: Optional[List[Handler]] = ..., bot: Any, **kwargs) -> BotClient: ...
