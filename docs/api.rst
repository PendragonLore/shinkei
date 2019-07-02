.. currentmodule:: shinkei

API Reference
=============

This sections outlines the shinkei API.


Client
------

.. autofunction:: connect

.. autoclass:: Client()
    :members:


.. _event_ref:

Event Reference
---------------

All the following events can be catched through :ref:`event handlers <event_handlers>`
or specific methods like :meth:`Client.wait_for` or :meth:`Client.stream`.


.. data:: data

    This event is fired whenever this client receives data from other clients trough
    :meth:`Client.send` and :meth:`Client.broadcast`.

    The only argument returned is the data represented as :class:`MetadataPayload`.

.. data:: ready

    This event is fire whenever the WebSocket has connected and successfully identified.

    No arguments are returned.

.. data:: error

    This event is fired whenever the WebSocket returns an error message.

    The only argument returned is the error message as a :class:`str`.

.. data:: connect

    This event is fired whenever the WebSocket has successfully connected.

    No arguments are returned.

.. data:: disconnect

    This event is fired whenever the WebSocket has disconnected.

    No arguments are returned.

.. _event_handlers:

Event Handlers
--------------

Events described in the :ref:`event reference <event_ref>` are handled through the proper handlers.

Event handlers are classes which subclass :class:`Handler` and have functions which listen to events decorated with
the :func:`listens_to`.

See the following piece of code for an example:

.. code-block:: python3

    class CustomHandler(shinkei.Handler, name="custom"):
        @shinkei.listens_to("data")
        async def data_receiver(self, data):
            print(f"{self.qualified_name} received {data.payload}!")


    # somewhere else...

    client = await shinkei.connect(..., handlers=[CustomHandler()])

Through this handler, every time the client receives data it will print ``custom received <data-here>!``

.. autoclass:: HandlerMeta
    :members:

.. autoclass:: Handler
    :members:

.. autodecorator:: listens_to

Query Builder
-------------

.. autoclass:: QueryBuilder
    :members:

.. autoclass:: Node
    :members:


Data Classes
------------

.. autoclass:: Version()

.. autoclass:: MetadataPayload()


Exceptions
----------

.. autoclass:: ShinkeiException()

.. autoclass:: ShinkeiHTTPException()

.. autoclass:: ShinkeiWSException()

.. autoclass:: ShinkeiResumeWS()

.. autoclass:: ShinkeiWSClosed()