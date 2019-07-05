import asyncio
from typing import Mapping, Optional, Set, Union

import aiohttp
# noinspection PyPackageRequirements
from yarl import URL

from .objects import Version
from .querybuilder import QueryBuilder


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
