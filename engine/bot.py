import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
import requests
import os
import re

load_dotenv()
ALLOWED_CHANNELS = os.environ['ALLOWED_CHANNELS']

intents = nextcord.Intents.default()
intents.message_content = True
intents.messages = True
client = commands.Bot(command_prefix='!', intents=intents)

COMMENTS_THREAD_NAME = "💬 Оставить комментарии"
GREETING_BOT_MESSAGE = "Создана ветка обсуждения"


def has_attached_image(message):
    if message.attachments:
        attachment = message.attachments[0]
        return attachment.content_type.startswith('image/')
    else:
        pattern = re.compile(r'(http|https)://\S+')
        if pattern.match(message.content):
            try:
                response = requests.head(message.content)
                if response.status_code == 200:
                    return 'image' in response.headers.get('content-type')
            except requests.exceptions.RequestException:
                return False


@client.event
async def on_message(message):
    if ALLOWED_CHANNELS and str(message.channel.id) not in ALLOWED_CHANNELS:
        return
    if message.author.bot:
        return

    if has_attached_image(message):
        try:
            thread = await message.create_thread(
                name=COMMENTS_THREAD_NAME,
                auto_archive_duration=60
            )
            await thread.send(GREETING_BOT_MESSAGE)
        except nextcord.errors.HTTPException as e:
            print(f'An error occurred while creating a thread: {e}')
        except Exception as e:
            print(f'An unexpected error occurred: {e}')


@client.event
async def on_ready():
    print(f'Logged in as: {client.user.name}')
