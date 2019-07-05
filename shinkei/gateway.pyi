from typing import List, Mapping, Optional, Union

import websockets
# noinspection PyPackageRequirements
from yarl import URL

from .client import Client
from .keepalive import KeepAlivePls
from .querybuilder import QueryBuilder

class WSClient(websockets.WebSocketClientProtocol):
    OP_HELLO: int
    OP_IDENTIFY: int
    OP_READY: int
    OP_INVALID: int
    OP_DISPATCH: int
    OP_HEARTBEAT: int
    OP_HEARTBEAT_ACK: int
    OP_GOODBYE: int

    client: Client
    auth: Optional[str]
    client_id: str
    app_id: str
    tags: Optional[List[str]]
    reconnect: bool
    keep_alive: KeepAlivePls
    hb_interval: float

    @classmethod
    async def create(cls, client: Client, url: URL, *, reconnect: bool) -> WSClient: ...

    @staticmethod
    def set_attrs(ws: WSClient, client: Client, *, reconnect: bool) -> None: ...

    async def poll_event(self) -> None: ...

    async def parse_payload(self, data: dict) -> None: ...

    def _dispatch(self, name: str, *args) -> None: ...

    async def identify(self) -> None: ...

    async def send_metadata(self, data: Union[str, dict, float, int, list], *, target: QueryBuilder,
                            nonce: Optional[str] = ...) -> None: ...

    async def broadcast_metadata(self, data: Union[str, dict, float, int, list], *, target: QueryBuilder,
                                 nonce: Optional[str] = ...) -> None: ...

    async def update_metadata(self, data: Mapping[str, dict], *, cache: Optional[bool] = ...) -> None: ...

    async def recv_json(self) -> dict: ...

    async def send_json(self, data: dict) -> None: ...
