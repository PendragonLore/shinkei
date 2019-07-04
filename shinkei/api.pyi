import asyncio

import aiohttp
from yarl import URL

from .querybuilder import QueryBuilder
from .objects import Version

try:
    import ujson as json
except ImportError:
    import json

from typing import Set, Union, Optional, Mapping


class APIClient:
    BODY_METHODS: Set[str]
    METHODS: Set[str]

    headers: dict

    session: aiohttp.ClientSession
    url: URL
    version: Version
    auth: Optional[str]

    @classmethod
    async def create(cls, url: URL, *, session: Optional[aiohttp.ClientSession] = ...,
                     auth: Optional[str] = ..., loop: Optional[asyncio.AbstractEventLoop] = ...) -> APIClient: ...

    async def request(self, method: str, url: URL, **kwargs: dict) -> dict: ...

    async def _fetch_version(self) -> dict: ...

    async def discovery_tags(self, tags: list) -> dict: ...

    async def proxy(self, method: str, route: str, *, target: QueryBuilder, body: Union[dict, str] = ...,
                    headers: Mapping[str, str] = ...): ...
