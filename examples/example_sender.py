import asyncio
import uuid

import shinkei


async def main():
    async with shinkei.connect("singyeong://localhost:4567", application_id="my-cool-app",
                               client_id=uuid.uuid4().hex, tags=["sender"]) as conn:
        # set some basic metadata
        await conn.update_metadata({"sender_id": {"type": "integer", "value": 1}})
        # target the first non restricted client found which has a receiver_id equal to 1
        # this will raise if no target is found.
        target = shinkei.QueryBuilder(application="my-cool-app", key="uniquekey").eq("receiver_id", 1)

        for number in range(10):
            await conn.send("Hi! (send number {0})".format(number), target=target)

            await asyncio.sleep(5)


asyncio.run(main())
