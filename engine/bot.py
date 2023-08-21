from collections import deque
from datetime import datetime, timedelta
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
import requests
import os
import re
from engine.content_moderator import is_image_nsfw

load_dotenv()
ALLOWED_CHANNELS = os.environ['ALLOWED_CHANNELS']

intents = nextcord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents)

COMMENTS_THREAD_NAME = "💬 Оставить комментарии"
GREETING_BOT_MESSAGE = "Создана ветка обсуждения"
MUTE_HEADER_MESSAGE = '❌ Здравствуйте, вам бан! ❌'
MUTE_REASONS = {'SPAM': "спамил картинками",
                'NSFW': "постил непотребства"}
MUTE_DESCRIPTION_MESSAGE = 'Теперь он улетает в мут, хорошенько подумать о своем поведении!'
TIMEOUT_DURATION = 9000
MAX_IMAGES = 7
TIME_LIMIT = 60

user_message_statistics = {}
active_timeout = {}


def get_attached_images_urls(message):
    attached_images_urls = []
    for attachment in message.attachments:
        if attachment.content_type.startswith('image/'):
            attached_images_urls.append(attachment.url)
    return attached_images_urls


def get_textarea_urls(message):
    url_pattern = re.compile(r'(http|https)://\S+')
    message_content_as_list = message.content.split("\n")
    urls = list(filter(lambda item: url_pattern.match(item), message_content_as_list))
    textarea_urls = []
    for url in urls:
        try:
            response = requests.head(url)
            if response.status_code == 200 and 'image' in response.headers.get('content-type'):
                textarea_urls.append(url)
        except requests.exceptions.RequestException:
            continue
    return textarea_urls


async def mute_user(message, reason):
    try:
        await message.author.timeout(timedelta(
            seconds=TIMEOUT_DURATION),
            reason=reason
        )
        print(f'User {message.author} has been muted.')
    except nextcord.errors.Forbidden:
        print(f'Privileged users cannot be muted by this bot!')


async def delete_message(message):
    try:
        await message.delete()
    except nextcord.errors.NotFound:
        print(f'Message not found or already deleted')


async def create_thread(message):
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


async def check_spam(message):
    user_id = message.author.id

    if user_id not in user_message_statistics:
        user_message_statistics[user_id] = deque(maxlen=MAX_IMAGES)
    user_message_statistics[user_id].append(message.created_at.timestamp())
    if user_id in user_message_statistics and len(user_message_statistics[user_id]) == MAX_IMAGES:
        oldest_message_time = user_message_statistics[user_id].popleft()
        current_time = message.created_at.timestamp()
        if current_time - oldest_message_time <= TIME_LIMIT:
            active_timeout[user_id] = {'channel': message.channel,
                                       'reason': MUTE_REASONS['SPAM']}
            await mute_user(message, MUTE_REASONS['SPAM'])
            spam_initial_time = datetime.fromtimestamp(current_time - TIME_LIMIT)
            async for item in message.channel.history(limit=None, after=spam_initial_time):
                if item.author == message.author:
                    await delete_message(item)
            user_message_statistics.pop(user_id, None)
            return True


async def check_nsfw(message, message_images_urls):
    user_id = message.author.id

    for image_url in message_images_urls:
        if await is_image_nsfw(image_url):
            active_timeout[user_id] = {'channel': message.channel,
                                       'reason': MUTE_REASONS['NSFW']}
            await mute_user(message, MUTE_REASONS['NSFW'])
            await delete_message(message)
            return True


@client.event
async def on_message(message):
    if message.author.bot:
        return

    message_images_urls = get_textarea_urls(message) + get_attached_images_urls(message)
    if message_images_urls:
        if not message.author.guild_permissions.administrator:
            is_spam = await check_spam(message)
            is_nsfw = await check_nsfw(message, message_images_urls)
            if is_spam or is_nsfw:
                return
        if ALLOWED_CHANNELS and str(message.channel.id) not in ALLOWED_CHANNELS:
            return
        await create_thread(message)


@client.event
async def on_member_update(before, after):
    if not before.communication_disabled_until and after.communication_disabled_until:
        if after.id in active_timeout.keys():
            channel = active_timeout[after.id]['channel']
            reason_for_muting = active_timeout[after.id]['reason']
            mute_info = nextcord.Embed(
                title=MUTE_HEADER_MESSAGE,
                description=f'Абоба {after.mention} {reason_for_muting}. '
                            f'{MUTE_DESCRIPTION_MESSAGE}',
                colour=nextcord.Colour.from_rgb(255, 0, 0)
            )
            await channel.send(embed=mute_info)
            active_timeout.pop(after.id, None)


@client.event
async def on_ready():
    print(f'Logged in as: {client.user.name}')
