import asyncio
import uuid

import shinkei


async def main():
    async with shinkei.connect("singyeong://localhost:4567", rest_dns="http://localhost:4567",
                               application_id="my-cool-app", client_id=uuid.uuid4().hex) as client:
        target = shinkei.QueryBuilder(application="my-cool-app", key="uniquekey", optional=True).eq("key1", "hithere")

        await client.send({"somekey": "somevalue"}, target=target)

        await asyncio.sleep(5)


@shinkei.Client.listen()
async def listen(data):
    print("I received this data:", data)


asyncio.run(main())
