import nextcord
from nextcord.ext import commands
import logging

COMMENTS_THREAD_NAME = "💬 Оставить комментарии"
GREETING_BOT_MESSAGE = "Создана ветка обсуждения"


class ThreadManager(commands.Cog):
    def __init__(self, client):
        self.client = client

    @staticmethod
    async def create_thread(message):
        try:
            thread = await message.create_thread(
                name=COMMENTS_THREAD_NAME,
                auto_archive_duration=60
            )
            await thread.send(GREETING_BOT_MESSAGE)
            logging.info(f"Создан тред для сообщения id:{message.id}, содержащим медиаконтент")
        except nextcord.errors.HTTPException as error:
            logging.error(f"При попытке создания треда возникла ошибка сетевого соединения: {error}.")
        except Exception as error:
            logging.error(f"При попытке создания треда возникла непредвиденная ошибка: {error}.")


def setup(client):
    client.add_cog(ThreadManager(client))
