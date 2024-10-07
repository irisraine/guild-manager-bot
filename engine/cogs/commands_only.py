import nextcord
from nextcord.ext import commands
import logging


class CommandsOnly(commands.Cog):
    def __init__(self, client):
        self.client = client

    @staticmethod
    async def check_is_command(message):
        if not message.content.startswith('/'):
            try:
                await message.delete()
            except nextcord.errors.NotFound:
                logging.warning("Сообщение не найдено, либо оно уже было удалено ранее.")


def setup(client):
    client.add_cog(CommandsOnly(client))
