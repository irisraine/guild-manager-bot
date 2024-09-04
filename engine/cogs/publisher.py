from nextcord.ext import commands
import logging


class Publisher(commands.Cog):
    def __init__(self, client):
        self.client = client

    @staticmethod
    async def publish_announcement_message(message):
        try:
            await message.publish()
            logging.info(f"Сообщение разослано по серверам, оформившим подписку на новостной канал '{message.channel}'")
        except Exception as error:
            logging.error(f"Ошибка при попытке осуществления рассылки сообщения: {error}")


def setup(client):
    client.add_cog(Publisher(client))
