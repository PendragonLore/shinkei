Quickstart
==========

This section is a quickstart to the library, explaining how to install it and showcasing some basic examples.

Installing
----------

shinkei is available on PyPi so it can be installed through pip:

.. code-block:: bash

    pip install shinkei -U

This library is compatible only with Python 3.6+ and has two main dependencies, `websockets <https://github.com/aaugustin/websockets>`_
and `aiohttp <https://github.com/aio-libs/aiohttp>`_.

It's also recommended to install `ujson <https://github.com/esnme/ultrajson>`_ for faster JSON encoding/decoding.

The library can be installed with this extra dependency through this command:

.. code-block:: bash

    pip install shinkei[ujson] -U


Example
-------

This first example showcases some basic communication between a sender and a receiver

Receiver:

.. code-block:: python3

    # basic imports
    import asyncio
    import uuid

    import shinkei


    async def main():
        # async context manager so as soon as the program exists it will close the connection
        async with shinkei.connect("singyeong://localhost:4567",
                                   application_id="my-cool-app", client_id=uuid.uuid4().hex, tags=["receiver"]) as conn:
            # set some basic metadata for routing purposes
            await conn.update_metadata({"receiver_id": {"type": "integer", "value": 1}})

            # report every data sent with this async iterator
            async for data in conn.stream("data"):
                print(f"Received {data.payload} from {data.sender}")


    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()

Sender:

.. code-block:: python3

    import asyncio
    import uuid

    import shinkei


    async def main():
        async with shinkei.connect("singyeong://localhost:4567",
                                   application_id="my-cool-app", client_id=uuid.uuid4().hex, tags=["sender"]) as conn:
            # target the first non restricted client found which has a receiver_id equal to 1
            # this will raise if no target is found.
            target = shinkei.QueryBuilder(application="my-cool-app", key="uniquekey").eq("receiver_id", 1)

            for number in range(10):
                await conn.send("Hi! (send number {0})".format(number), target=target)

                await asyncio.sleep(5)


    asyncio.run(main())


With both of these scripts running, whenever the sender sends a message it will be routed to the receiver and printed,
due to it being the only client connected to the same app with a receiver_id equal to 1.
