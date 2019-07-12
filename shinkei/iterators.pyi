import abc
from typing import Any, Callable, Optional, Union

from .client import Client

class AbstractAsyncIterator(metaclass=abc.ABCMeta):
    def __aiter__(self) -> AbstractAsyncIterator: ...

    async def __anext__(self) -> Any: ...

    @abc.abstractmethod
    async def next(self): ...


class StreamAsyncIterator(AbstractAsyncIterator):
    _client: Client
    _event: str
    _timeout: Union[int, float]
    _check: Optional[Callable[..., bool]]
    _limit: Optional[int]
    _count: int

    def __init__(self, client: Client, event: str, *, timeout: Optional[Union[int, float]] = ...,
                 check: Optional[Callable[..., bool]] = ..., limit: Optional[int] = ...) -> None: ...

    async def next(self) -> Any: ...
