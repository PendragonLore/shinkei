# -*- coding: utf-8 -*-

import asyncio
import logging
import traceback

import websockets
# noinspection PyPackageRequirements
from yarl import URL

from .api import APIClient
from .backoff import ExponentialBackoff
from .exceptions import ShinkeiResumeWS, ShinkeiWSClosed
from .gateway import WSClient
from .handlers import Handler

log = logging.getLogger(__name__)


def connect(url, application_id, client_id, auth=None, *,
            tags=None, reconnect=True, session=None, loop=None, klass=None, handlers=None, **kwargs):
    """Connect to singyeong.

    Since this returns a context manager mixin of :class:`Client`, both

    .. code-block:: python3

        async with shinkei.connect(*args, **kwargs):
            # ....

    and

    .. code-block:: python3

        client = await shinkei.connect(*args, **kwargs):

        try:
            # ...
        finally:
            await client.close()

    are valid and do the same thing.

    Arguments
    ---------
    url: :class:`str`
        The base url for the WebSocket url.
    application_id: :class:`str`
        A unique id which should be shared among all related clients.
    client_id: :class:`str`
        An id unique across all clients connected to the same application.
    auth: Optional[:class:`str`]
        A password used to access the server.
        If an incorrect password is sent the client will be in restricted mode.
        Defaults to ``None``.
    tags: Optional[:class:`list`]
        A list of tags to identify the client and to allow the discovery of it's application id.
        If the client is restricted the tags will be ignored.
    reconnect: Optional[:class:`bool`]
        Whether or not to reconnect when singyeong sends a GOODBYE payload or when the
        WebSocket disconnects for other reasons.
        Defaults to ``True``
    handlers: Optional[List[:class:`Handler`]]
        The initial handlers to register.
    session: Optional[:class:`aiohttp.ClientSession`]
        The session used for HTTP requests.
        If none is provided, a new one will be created.
    loop: Optional[:class:`asyncio.AbstractEventLoop`]
        The loop used to connect to the websocket and make HTTP requests.
        If non is provided, :func:`asyncio.get_event_loop` will be used to get one.
    klass: Optional[:class:`type`]
        The classed used to instantiate the client.
        Defaults to :class:`Client`
    kwargs
        All other kwargs will be passed onto the Client class' ``_connect`` method.
        Useful when passing a custom class.
    Returns
    -------
    A context manager mixin of :class:`Client`
        The client."""
    return _ClientMixin(url, application_id, client_id, auth, reconnect=reconnect,
                        session=session, loop=loop, tags=tags, klass=klass, handlers=handlers, **kwargs)


# noinspection PyProtectedMember
class Client:
    # noinspection PyUnresolvedReferences
    """The main client connecting to singyeong.

        This is not supposed to be instantiated manually
        but through :func:`connect`

        Attributes
        ----------
        loop: :class:`asyncio.AbstractEventLoop`
            The loop used to connect to the websocket make HTTP requests.
        session: :class:`aiohttp.ClientSession`
            The aiohttp session used for HTTP requests.
        restricted: :class:`bool`
            Whether or not the client is restricted.
            A client is restricted usually when it fails to provide
            the right password.
        version: :class:`Version`
            A :class:`Version` object representing the singyeong and api version."""

    def __init__(self):
        self.handlers = {}
        self._waiters = {}

        self._internal_cache = []
        self._closed_event = asyncio.Event()
        self.schema_map = {"singyeong": "ws", "ssingyeong": "wss"}

    @classmethod
    async def _connect(cls, url, application_id, client_id, auth=None, *, reconnect=True,
                       session=None, loop=None, tags=None, handlers=None, **_):
        self = cls()

        if handlers is not None:
            for handler in handlers:
                self.add_handler(handler)

        self.loop = loop or asyncio.get_event_loop()

        self.auth = auth
        self.id = client_id
        self.app_id = application_id
        self.tags = tags

        ws_url = (URL(url) / "gateway" / "websocket").with_query("encoding=json")
        scheme = self.schema_map.get(ws_url.scheme, ws_url.scheme)

        self.ws_url = ws_url.with_scheme(scheme)
        self.reconnect = reconnect

        coro = WSClient.create(self, self.ws_url, reconnect=self.reconnect)
        self._ws = await asyncio.wait_for(coro, timeout=20)

        rest_scheme = "https" if self.ws_url.scheme == "wss" else "http"
        self._rest = await APIClient.create(URL(url).with_scheme(rest_scheme),
                                            session=session, auth=auth, loop=self.loop)

        self.version = self._rest.version

        self._task = self.loop.create_task(self._poll_data())

        return self

    @property
    def is_closed(self):
        """:class:`bool`: Whether or not the client is closed."""
        return self._closed_event.is_set()

    @property
    def latency(self):
        """:class:`float`: The latency, is seconds, between heartbeats."""
        return self._ws.keep_alive.latency

    async def send(self, data, *, target, nonce=None):
        """Send data to a client which matches the predicates of the ``target`` query.

        Restricted clients cannot use this method.

        Arguments
        ---------
        data: Union[:class:`str`, :class:`int`, :class:`float`, :class:`list`, :class:`dict`]
            The data to send.
            Must be JSON serializable.
        target: :class:`QueryBuilder`
            The query that is used to match the client.
        nonce
            A value used to identify the data sent.
                Raises
        ------
        ShinkeiWSException
            The client is restricted."""
        return await self._ws.send_metadata(data, target=target, nonce=nonce)

    async def broadcast(self, data, *, target, nonce=None):
        """Send data to all clients which matches the predicates of the ``target`` query.

        Restricted clients cannot use this method.

        Arguments
        ---------
        data: Union[:class:`str`, :class:`int`, :class:`float`, :class:`list`, :class:`dict`]
            The data to send.
            Must be JSON serializable.
        target: :class:`QueryBuilder`
            The query that is used to match the clients.
        nonce
            A value used to identify the data sent.

        Raises
        ------
        ShinkeiWSException
            The client is restricted."""
        return await self._ws.broadcast_metadata(data, target=target, nonce=nonce)

    async def update_metadata(self, data, *, cache=True):
        """Update metadata on singyeong.

        The data is not consistent between server restarts but
        if ``cache`` is set to ``True`` then it will be persist between restarts.

        ``data`` must have a structure similar to the following dictionary:

        .. code-block:: python3

            {
              "key": {
                "value": "hi!",
                "type": "string",
              },
              "key2": {
                "value": 123,
                "type": "integer",
              },
            }

        ``data`` keys cannot be one of ``ip``, ``restricted``, ``encoding`` or ``last_heartbeat_time``.
        Valid ``type`` keys are ``string``, ``integer``, ``float``, ``list`` and
        ``version`` see `here <https://hexdocs.pm/elixir/Version.html>`_ for specifications.

        Arguments
        ---------
        data: :class:`dict`
            The metadata to update.
            Must be JSON serializable.
        cache: Optional[:class:`bool`]
            Whether or not to cache the metadata and send it back on reconnects.
            Defaults to ``True``.
        Raises
        ------
        ShinkeiWSException
            The metadata structure was invalid or a restricted key was used."""
        return await self._ws.update_metadata(data, cache=cache)

    async def proxy_request(self, method, route, *, target, body=None, headers=None):
        """Make a proxy HTTP request to a client.

        Arguments
        ---------
        method: :class:`str`
            The HTTP method to use.
            Supports only POST, PATCH, PUT, DELETE, MOVE, GET and HEAD.
        route: :class:`str`
            The route to make the request to.
        body: Optional
            The request body, silently ignored in GET and HEAD.
            If none is provided but the method requires one an empty string will be sent.
        headers: Optional[Mapping[:class:`str`, :class:`str`]]
            The request headers.
        target: :class:`QueryBuilder`
            The query that is used to match the client.

        Returns
        -------
        The HTTP response.

        Raises
        ------
        ValueError
            An unsupported request method was passed.
        ShinkeiHTTPException
            The HTTP proxy request failed."""
        return await self._rest.proxy(method, route, target=target, headers=headers, body=body)

    async def discover(self, tags):
        """Discover an application id by it's clients tags.

        Arguments
        ---------
        tags: :class:`list`
            The list of tags an application client must have to match

        Returns
        -------
        :class:`list`
            A list of application ids matching.

        Raises
        ------
        TypeError
            The ``tags`` argument wasn't a :class:`list`."""
        ret = await self._rest.discovery_tags(tags)

        return ret.get("result")

    def add_handler(self, handler):
        """A function used to manually add handler to the client.

        Arguments
        ---------
        handler: :class:`Handler`
            The handler to add.

        Returns
        -------
        :class:`Handler`
            The handler added.

        Raises
        ------
        TypeError
            ``handler`` was not an instance of :class:`Handler`
        ValueError
            The handler was already registered.
            This is determined by the name of the handler."""
        if not isinstance(handler, Handler):
            raise TypeError("handler must be an instance of Handler, got {0}".format(handler.__class__.__name__))
        name = handler.qualified_name
        if name in self.handlers:
            raise ValueError(f"Handler {name} is already registered.")
        self.handlers[name] = ret = handler

        return ret

    def remove_handler(self, handler_name):
        """Remove a handler by name.

        Arguments
        ---------
        handler_name: :class:`str`
            The name of the handler.

        Returns
        -------
        Optional[:class:`Handler`]
            The handler, or ``None`` if it wasn't removed."""
        return self.handlers.pop(handler_name, None)

    async def wait_for(self, event, *, timeout=None, check=None):
        """Wait for an event.

        Arguments
        ---------
        event: :class:`str`
            The name of the event.
        timeout: Optional[Union[:class:`int`, :class:`float`]]
            The amount of time to wait before timing out.
            By default it never times out.
        check: Optional[Callable[..., :class:`bool`]]
            A callable which returns a falsy or truthy value to filter
            the event to wait for.

        Returns
        -------
        Any
            The return value of the event."""
        future = self.loop.create_future()

        if check is None:
            def check(*_, **__):
                return True

        self._waiters.setdefault(event.lower(), []).append((future, check))

        return await asyncio.wait_for(future, timeout=timeout)

    async def stream(self, event, *, timeout=None, check=None, limit=None):
        """An async iterator which waits until an event is dispatched before
        continuing the iterations.

        Arguments
        ---------
        event: :class:`str`
            Same as :meth:`Client.wait_for`.
        timeout: Optional[Union[:class:`int`, :class:`float`]]
            Same as :meth:`Client.wait_for`.
        check: Optional[Callable[..., :class:`bool`]]
            Same as :meth:`Client.wait_for`.
        limit: Optional[:class:`int`]
            The maximum amount of iteration before the iterator stops.
            By default it never stops.

        Yields
        ------
        Any
            The return value of the event."""
        count = 1

        while True if limit is None else count <= limit:
            if limit is not None:
                count += 1

            yield await self.wait_for(event, timeout=timeout, check=check)

    async def close(self):
        """Close the connection to singyeong.

        Run this when cleaning up."""
        self._closed_event.set()
        if not self._rest.session.closed:
            await self._rest.session.close()
        self._ws.keep_alive.stop()
        await self._ws.close(1000)

    async def _do_poll(self):
        try:
            await self._ws.poll_event()
        except ShinkeiResumeWS as exc:
            self._ws._dispatch("disconnect")
            if not self.reconnect:
                log.info("%s, disconnecting.", exc.message)
                self._task.cancel()
                await self.close()
                return
            log.info("%s, trying to reconnect.", exc.message)
            coro = WSClient.create(self, self.ws_url, reconnect=self.reconnect)

            self._ws = await asyncio.wait_for(coro, timeout=20.0, loop=self.loop)

    async def _poll_data(self):
        backoff = ExponentialBackoff()

        while True:
            # noinspection PyBroadException
            try:
                await self._do_poll()
            except asyncio.CancelledError:
                raise
            except (OSError,
                    ValueError,
                    asyncio.TimeoutError,
                    websockets.InvalidHandshake,
                    websockets.WebSocketProtocolError,
                    ShinkeiWSClosed,
                    websockets.InvalidMessage) as exc:
                self._ws._dispatch("disconnect")
                if not self.reconnect:
                    await self.close()
                    if isinstance(exc, ShinkeiWSClosed) and exc.code == 1000:
                        log.info("Websocket closed successfully.")
                        return
                    log.warning("Websocket closed forcefully.")
                    traceback.print_exc()
                    raise

                if self.is_closed:
                    log.info("Websocket closed successfully.")
                    return

                if isinstance(exc, ShinkeiWSClosed):
                    if not exc.code == 1000:
                        await self.close()
                        log.warning("Websocket closed forcefully.")
                        traceback.print_exc()
                        raise

                delay = backoff.delay()
                log.debug("Trying to reconnect in %.2fs.", delay)
                await asyncio.sleep(delay, loop=self.loop)
            except Exception:
                traceback.print_exc()


# noinspection PyProtectedMember
class _ClientMixin:
    __slots__ = ("_args", "_kwargs", "_client", "_client_class")

    def __init__(self, *args, **kwargs):
        self._client_class = kwargs.pop("klass", None) or Client
        self._args = args
        self._kwargs = kwargs

        self._client = None

    def __await__(self):
        return self._client_class._connect(*self._args, **self._kwargs).__await__()

    async def __aenter__(self):
        self._client = await self._client_class._connect(*self._args, **self._kwargs)

        return self._client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.close()
