import asyncio
import uuid

import shinkei


async def main():
    async with shinkei.connect("singyeong://localhost:4567", rest_dns="http://localhost:4567",
                               application_id="my-cool-app", client_id=uuid.uuid4().hex, tags=["hi"],
                               auth="2d1e29fbe6895b3693112ff<insert more long password here>") as conn:
        # set some basic metadata
        await conn.update_metadata({"hi": {"type": "integer", "value": 123}})

        # "Hi me!" will be sent to the first client which "hi" metadata key equals to 123
        # aka the current client
        target = shinkei.QueryBuilder(application="my-cool-app", key="uniquekey", optional=False).eq("hi", 123)
        await conn.send("Hi me!", target=target)

        await asyncio.sleep(5)


@shinkei.Client.listen()
async def listen(data):
    # once the data is sent this will print "I received this data: Hi me! from <current UUID>"
    print(f"I received this data: {data.payload} from {data.sender}")


asyncio.run(main())
