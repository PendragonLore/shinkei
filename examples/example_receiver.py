import asyncio
import uuid

import shinkei


class SimpleEventHandler(shinkei.Handler):
    @shinkei.listens_to("data")
    async def data_receiver(self, data):
        print("{0.qualified_name} received {1.payload}".format(self, data))


async def main():
    client = await shinkei.connect("singyeong://localhost:4567", application_id="my-cool-app",
                                   client_id=uuid.uuid4().hex, tags=["receiver"], handlers=[SimpleEventHandler()])
    await client.update_metadata({"receiver_id": 1})

    async for data in client.stream("data", limit=5):
        print("Stream received {0.payload}".format(data))


loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
