import asyncio

import shinkei
import uuid


async def main():
    client = await shinkei.Client.connect("singyeong://localhost:4567", rest_dns="http://localhost:4567",
                                          application_id="my-cool-app", client_id=uuid.uuid4().hex)

    # optional will always return the data regardless if the query was successful
    target = shinkei.QueryBuilder(application_id="my-cool-app", key="uniquekey", optional=True).eq("key1", "hithere")
    for _ in range(5):
        await client.send({"somekey": "somevalue"}, target=target)

        await asyncio.sleep(20)

    await client.close()


@shinkei.Client.listen()
async def listen(data):
    print("I received this data:", data)


asyncio.run(main())
