Bot Quickstart
==============

This quickstart showcases an example of how to use shinkei in a discord bot made with discord.py


.. code-block:: python3

    import uuid

    import shinkei
    from discord.ext import commands


    class MyBot(commands.Bot):
        def __init__(self, *args, **kwargs):
            self.ipc = None

            super().__init__(*args, **kwargs)

        async def login(self, token, *, bot=True):
            """Connect to singyeong before the bot starts.

            If anything raises here it will stop the bot from starting so be careful."""
            self.ipc = await shinkei.connect("singyeong://localhost:4567", rest_url="http://localhost:4567",
                                             application_id="my-cool-bot", client_id=uuid.uuid4().hex, tags=["receiver"],
                                             klass=shinkei.ext.BotClient, bot=self)

            await self.ipc.update_metadata({"shard_id": {"type": "integer", "value": self.shard_id}})

            return await super().login(token, bot=bot)

        async def on_shinkei_data(self, data):
            """Receiving data is handled by bot.dispatch() and so this is possible."""
            print(f"I received this data {data.payload} from {data.sender}")

        async def send_to_shard(self, data, shard_id):
            """Send data to another shard in a different process.

            For example, you could notify other shards of DMs if this process is running on shard 0."""
            target = shinkei.QueryBuilder(application="my-cool-bot", key="uniquekey").eq("shard_id", shard_id)

            await self.ipc.send(data, target=target)


    bot = MyBot(command_prefix="!", shard_id=0, shard_count=2)

    bot.run("token")

This same example could be ran in another process with a different shard id to allow ipc between shards.