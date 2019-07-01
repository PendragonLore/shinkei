import asyncio
import uuid

import shinkei


async def main():
    client = await shinkei.connect("singyeong://localhost:4567", rest_url="http://localhost:4567",
                                   application_id="my-cool-app", client_id=uuid.uuid4().hex, tags=["receiver"])

    await client.update_metadata({"receiver_id": {"type": "integer", "value": 1}})


@shinkei.Client.listen()
async def listener(data):
    print("I received this data: {0.payload} from {0.sender}".format(data))


loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
