import asyncio
from types import TracebackType
from typing import Optional, Type, List, Mapping, Union, Any, Callable, Iterable, Coroutine, AsyncGenerator

import aiohttp
from yarl import URL

from .api import APIClient
from .gateway import WSClient
from .handlers import Handler
from .objects import Version
from .querybuilder import QueryBuilder


def connect(url: str, application_id: str, client_id: str,
            auth: Optional[str] = ..., *, tags: Optional[list] = ..., reconnect: Optional[bool] = ...,
            session: Optional[aiohttp.ClientSession] = ..., loop: Optional[asyncio.AbstractEventLoop] = ...,
            klass: Optional[Type[Client]] = ..., handlers: Optional[List[Handler]] = ...,
            **kwargs) -> _ClientMixin: ...


class Client:
    _waiters: dict
    _internal_cache: list
    _closed_event: asyncio.Event

    handlers: dict
    schema_map: Mapping[str, str]

    loop: asyncio.AbstractEventLoop
    id: str
    app_id: str
    auth: Optional[str]
    tags: List[str]
    reconnect: bool
    ws_url: URL
    restricted: bool

    _ws: WSClient
    _rest: APIClient

    version: Version

    _task: asyncio.Task

    @property
    def is_closed(self) -> bool: ...

    @property
    def latency(self) -> bool: ...

    @classmethod
    async def _connect(cls, url: str, application_id: str, client_id: str,
                       auth: Optional[str] = ..., *, tags: Optional[list] = ..., reconnect: Optional[bool] = ...,
                       session: Optional[aiohttp.ClientSession] = ..., loop: Optional[asyncio.AbstractEventLoop] = ...,
                       handlers: Optional[List[Handler]] = ...,
                       **_) -> Client: ...

    async def send(self, data: Union[str, dict, float, int, list], *, target: QueryBuilder,
                   nonce: Any = ...) -> None: ...

    async def broadcast(self, data: Union[str, dict, float, int, list], *, target: QueryBuilder,
                        nonce: Any = ...) -> None: ...

    async def update_metadata(self, data: Mapping[str, dict]) -> None: ...

    async def proxy_request(self, method: str, route: str, *, target: QueryBuilder,
                            body: Optional[Union[str, dict, list]]) -> Any: ...

    async def discover(self, tags: list) -> list: ...

    def add_handler(self, handler: Handler) -> Handler: ...

    def remove_handler(self, handler_name: str) -> Handler: ...

    async def wait_for(self, event: str, *, timeout: Optional[Union[int, float]] = ...,
                       check: Optional[Callable[..., bool]] = ...) -> Any: ...

    async def stream(self, event: str, *, timeout: Optional[Union[int, float]] = ...,
                     check: Optional[Callable[..., bool]] = ..., limit: Optional[int] = ...) -> AsyncGenerator[Any]: ...

    async def close(self) -> None: ...

    async def _do_poll(self) -> None: ...

    async def _poll_data(self) -> None: ...


class _ClientMixin:
    __slots__: Iterable[str]

    _client_class: Type[Client]
    _args: tuple
    _kwargs: dict
    _client: Optional[Client]

    def __init__(self, url: str, application_id: str, client_id: str,
                 auth: Optional[str] = ..., *, tags: Optional[list] = ..., reconnect: Optional[bool] = ...,
                 session: Optional[aiohttp.ClientSession] = ..., loop: Optional[asyncio.AbstractEventLoop] = ...,
                 handlers: Optional[List[Handler]] = ...,
                 **kwargs) -> None: ...

    def __await__(self) -> Coroutine: ...

    async def __aenter__(self) -> Client: ...

    async def __aexit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException],
                        exc_tb: Optional[TracebackType]) -> None: ...
