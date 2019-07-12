import abc

from .exceptions import NoMoreItems


class AbstractAsyncIterator(metaclass=abc.ABCMeta):
    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            item = await self.next()
        except NoMoreItems:
            raise StopAsyncIteration()
        else:
            return item

    @abc.abstractmethod
    async def next(self):
        raise NotImplementedError("Must be implemented by subclasses.")


class StreamAsyncIterator(AbstractAsyncIterator):
    def __init__(self, client, event, *, timeout=None, check=None, limit=None):
        self._client = client

        self._event = event
        self._timeout = timeout
        self._check = check
        self._limit = limit

        self._count = 0

    async def next(self):
        if self._limit is not None:
            if self._count >= self._limit:
                raise NoMoreItems()
            self._count += 1

        item = await self._client.wait_for(self._event, timeout=self._timeout, check=self._check)

        return item
