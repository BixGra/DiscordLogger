from io import BytesIO

import discord


class DiscordClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

    async def on_ready(self):
        print(f"We have logged in as {self.user}")

    async def send_log(self, channel_id: int, message: str):
        await self.get_channel(channel_id).send(message)

    async def send_graph(self, channel_id: int, graph: BytesIO):
        await self.get_channel(channel_id).send(
            file=discord.File(graph, filename="volumes.png")
        )

    async def send_graphs(self, graphs: list[tuple[int, BytesIO]]):
        for channel_id, graph in graphs:
            await self.send_graph(channel_id=channel_id, graph=graph)
